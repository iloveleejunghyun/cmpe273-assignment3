
# def cache(ctype):
#     print(f'ctype={ctype}')

#     def cache_decorator(func):
#         def wrapped_function(*args, **kwargs):

#             return func(*args, **kwargs)
#     return cache_decorator


# @cache('put')
# def put(user):
#     print('exe in user')
#     pass


# put('a user')


# # fn参数用来做回调函数
# def lru_cache(fn):

#     # 需要inner 函数的原因是，不能让这段代码直接执行。 而是调用foo的时候才执行。
#     def wrapper():

#         print("hello, %s" % fn.__name__)

#         fn()

#         print("goodby, %s" % fn.__name__)

#     return wrapper

# # 本质是decorator执行，把下面被修饰的函数地址当做参数穿进去
# # ？1这是高阶函数。什么是高阶函数？返回了一个函数地址。
# # 如果decorator有参数，则把函数地址防到最后。
# @lru_cache
# def foo():

#     print("i am foo")


# foo()


# def makeHtmlTag(tag, *args, **kwds):

#     def real_decorator(fn):

#         css_class = " class='{0}'".format(
#             kwds["css_class"]) if "css_class" in kwds else ""

#         def wrapped(*args, **kwds):

#             return "<"+tag+css_class+">" + fn(*args, **kwds) + "</"+tag+">"

#         return wrapped

#     return real_decorator


# @makeHtmlTag(tag="b", css_class="bold_css")
# def hello():

#     return "hello world"


# print(hello())

import functools
import queue


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


cache_data = CacheDict()


def lru_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
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


@lru_cache
def put(key, user, data_bytes):
    print('put to remote server')
    return key


@lru_cache
def get(key, data_bytes):
    print('get from remote server')
    return 'an user' + key


@lru_cache
def delete(key, data_bytes):
    print('delete from remote server')
    return key


print(get("1001", 'send get data'))
print(put("1001", "an user", "send put data"))
print(put("1001", "an user", "send put data"))
print(get("1001", 'send get data'))
print(get("1002", 'send get data'))
print(delete("1001", 'send delete data'))
print(delete("1001", 'send delete data'))
