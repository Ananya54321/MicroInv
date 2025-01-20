from redis_om import HashModel

class TestModel(HashModel):
    name: str
    age: int

print("Redis OM is working!")
