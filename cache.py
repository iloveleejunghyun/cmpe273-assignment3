
import queue
import functools


class CacheDict(dict):
    cache_queue = queue.Queue(5)

    def __init__(self):
        self = dict()

    def put(self, key, value):
        if len(self) == 5:
            # remove one
            remove_key = self.cache_queue.pop()
            del self[remove_key]
        self[key] = value
        self.cache_queue.put(key)
        return key


cache_data = None


def lru_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global cache_data
        if cache_data == None:
            cache_data = CacheDict()

        if func.__name__ == 'put':
            user_id = args[0]
            user = cache_data.get(user_id)
            if not user:
                user = args[1]
                cache_data[user_id] = user
                print(
                    f'put id={user_id}, val={user} in cache and put it to server')
                return func(*args, **kwargs)
            print(
                f'already have id={user_id}, val={user} in cache, not put to server')
            return user_id  # todo check
        elif func.__name__ == 'get':
            user_id = args[0]
            user = cache_data.get(user_id)
            if not user:
                return func(*args, **kwargs)
            print(
                f'get: already have id={user_id}, val={user} in cache, not get it from server')
            return user
        elif func.__name__ == 'delete':
            user_id = args[0]
            user = cache_data.get(user_id)
            if user:
                del cache_data[user_id]
                print(
                    f'delete id={user_id}, val={user} from cache and delete it from server')
                return func(*args, **kwargs)
            print(
                f'no id={user_id}, val={user} in cache, not delete from server')
            return 'success'
        else:
            print(f'unknown exe:{func.__name__}')
            return func(*args, **kwargs)

    return wrapper
