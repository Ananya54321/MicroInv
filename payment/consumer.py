from main import redis, Order  # Import from db.py
import time
from fastapi import FastAPI

from redis_om import get_redis_connection, HashModel


key = 'refund_order'
group = 'payment-group'

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists!")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                order = Order.get(obj['pk'])
                order.status = 'refunded'
                order.save()
                
        # print(results)
    except Exception as e:
        print(str(e))
    time.sleep(1)
