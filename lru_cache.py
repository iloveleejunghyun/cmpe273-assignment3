
import queue
import functools
import time


class CacheDict(dict):

    def __init__(self, size):
        dict.__init__(self)
        # self = dict()
        self.cache_queue = queue.Queue(size)
        self.cache_size = size

    def put(self, key, value):
        if len(self) == self.cache_size:
            # remove one
            remove_key = self.cache_queue.get()
            del self[remove_key]
        self[key] = value
        self.cache_queue.put(key)
        return key


cache_data = None


def lru_cache(size):
    global cache_data
    if cache_data == None:
        cache_data = CacheDict(size)

    def cache_decorator(func):
        def wrapper(*args, **kwargs):
            # print('[%s] %s()...' % (size, func.__name__))
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
            elif func.__name__ == 'fibonacci':
                param = args[0]
                value = cache_data.get(param)
                if value:
                    print(f"[cache-hit] fibonacci({param}) -> {value} ")
                else:
                    value = func(*args, **kwargs)
                    cache_data.put(param, value)
                    print(
                        f"[{time.perf_counter()}] fibonacci({param}) -> {value} ")
                return value
            else:

                print(f'unknown exe:{func.__name__}')
            return func(*args, **kwargs)
        return wrapper
    return cache_decorator

# def lru_cache(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         global cache_data
#         if cache_data == None:
#             cache_data = CacheDict()

#         if func.__name__ == 'put':
#             user_id = args[0]
#             user = cache_data.get(user_id)
#             if not user:
#                 user = args[1]
#                 cache_data[user_id] = user
#                 print(
#                     f'put id={user_id}, val={user} in cache and put it to server')
#                 return func(*args, **kwargs)
#             print(
#                 f'already have id={user_id}, val={user} in cache, not put to server')
#             return user_id  # todo check
#         elif func.__name__ == 'get':
#             user_id = args[0]
#             user = cache_data.get(user_id)
#             if not user:
#                 return func(*args, **kwargs)
#             print(
#                 f'get: already have id={user_id}, val={user} in cache, not get it from server')
#             return user
#         elif func.__name__ == 'delete':
#             user_id = args[0]
#             user = cache_data.get(user_id)
#             if user:
#                 del cache_data[user_id]
#                 print(
#                     f'delete id={user_id}, val={user} from cache and delete it from server')
#                 return func(*args, **kwargs)
#             print(
#                 f'no id={user_id}, val={user} in cache, not delete from server')
#             return 'success'
#         else:
#             print(f'unknown exe:{func.__name__}')
#             return func(*args, **kwargs)

#     return wrapper
