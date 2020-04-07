import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

# redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
# redis_url = os.getenv('REDISTOGO_URL', 'redis://redistogo:78d62750fe7a926bceed7828fd46c454@crestfish.redistogo.com:11719/')
redis_url = "redis://redistogo:78d62750fe7a926bceed7828fd46c454@crestfish.redistogo.com:11719/"
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
