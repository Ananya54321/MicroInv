from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    host="redis-14374.c305.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=14374,
    password="wIq1RlAVXW5ERNLgfWFFQYe8Ph9W2Z4S",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity_available: int

    class Meta:
        database = redis

# Define a Pydantic model for request validation
class ProductRequest(BaseModel):
    name: str
    price: float
    quantity_available: int

@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]

@app.post('/products')
def create(product: ProductRequest):
    # Convert Pydantic model into HashModel
    new_product = Product(
        name=product.name,
        price=product.price,
        quantity_available=product.quantity_available
    )
    return new_product.save()

def format(pk : str):
    product = Product.get(pk)

    return{
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity_available': product.quantity_available
    }

@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)

@app.delete('/products/{pk}')
def delete(pk : str):
    return Product.delete(pk)
