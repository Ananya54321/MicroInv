from main import redis, Product  # Import from db.py
import time
from fastapi import FastAPI

from redis_om import get_redis_connection, HashModel


key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists!")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)
        if results != []:
            print(results)
            for result in results:
                obj = result[1][0][1]
                try:
                    product = Product.get(obj['product_id'])
                    product.quantity_available -= int(obj['quantity'])
                    product.save()
                except:
                    redis.xadd('refund_order', obj, '*')
        # print(results)
    except Exception as e:
        print(str(e))
    time.sleep(1)
