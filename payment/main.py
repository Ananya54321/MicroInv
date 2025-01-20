from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from pydantic import BaseModel
from starlette.requests import Request
import time
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis database connection
redis = get_redis_connection(
    host="redis-14374.c305.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=14374,
    password="wIq1RlAVXW5ERNLgfWFFQYe8Ph9W2Z4S",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis


@app.get('/orders/{pk}')
def get_order(pk: str):
    """
    Retrieve an order by its primary key.
    """
    try:
        order = Order.get(pk)
        return order
    except Exception as e:
        return {"error": f"Order not found. Details: {str(e)}"}


@app.post('/orders')
async def create_order(request: Request, background_tasks: BackgroundTasks):
    """
    Create a new order and process it in the background.
    """
    body = await request.json()
    try:
        # Fetch product details from another service
        response = requests.get(f"http://localhost:8001/products/{body['id']}")
        response.raise_for_status()
        product = response.json()

        # Create a new order
        order = Order(
            product_id=body['id'],
            price=product['price'],
            fee=0.2 * product['price'],
            total=1.2 * product['price'],
            quantity=body['quantity'],
            status='pending'
        )
        order.save()

        # Add order processing to background tasks
        background_tasks.add_task(order_completed, order)

        return order
    except requests.RequestException as e:
        return {"error": f"Failed to fetch product details. Details: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred while creating the order. Details: {str(e)}"}


def order_completed(order: Order):
    """
    Simulate order processing and mark the order as completed.
    """
    try:
        # Simulate order processing delay
        time.sleep(5)

        # Update the order status
        order.status = 'completed'
        order.save()

        # Notify other services via Redis stream
        redis.xadd('order_completed', order.dict(), '*')
    except Exception as e:
        print(f"Error in completing order: {str(e)}")
