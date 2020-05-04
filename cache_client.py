import sys
import socket
import time
import queue

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, deserialize, serialize_DELETE
from node_ring import NodeRing
from pybloom import BloomFilter

BUFFER_SIZE = 1024


class UDPClient():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

    def send(self, request):
        print('Connecting to server at {}:{}'.format(self.host, self.port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(request, (self.host, self.port))
            response, ip = s.recvfrom(BUFFER_SIZE)
            return response
        except socket.error:
            print("Error! {}".format(socket.error))
            exit()


ring = NodeRing(nodes=[0, 1, 2, 3])
clients = []
# node = ring.get_node('9ad5794ec94345c4873c4e591788743a')


# class CacheDict(dict):
#     cache_queue = queue.Queue(5)
#     def __init__(self):
#         self = dict()


#     def put(self, key, value):
#         if len(self) == 5:
#             #remove one
#             remove_key =  self.cache_queue.pop()
#             del self[remove_key]
#         self[key] = value
#         self.cache_queue.put(key)
#         return key

# cache_data = CacheDict()

# bloom = BloomFilter(100, 0.001)

# def is_member(key):
#     return key in bloom

# def add_member(key):
#     bloom.add(key)

# def cache(ctype):
#     def cache_decorator(func):
#         # @wraps(func)
#         def wrapped_function(*args, **kwargs):
#             log_string = func.__name__ + " was called"
#             print(log_string)
#             # do sth
#             if ctype == 'put':
#                 data_bytes, key = serialize_PUT(args[1])

#                 cache_data.put(key, data_bytes)
#                 return func(*args, **kwargs)

#                 return 'success'
#             elif ctype == 'get':
#                 data = cache_data.get(key)
#                 if not data:
#                     return data
#                 else:
#                     #todo if add result to cache?
#                     return func(*args, **kwargs)
#             elif ctype == 'delete':

#                 del cache_data[key]
#                 #todo  delete from bloom filter
#                 return func(*args, **kwargs)
#         return wrapped_function
#     return cache_decorator

# @cache('put')
def put(key, user, data_bytes):
    # if not is_member(user):
    #    add_member(user)
    # hash
    fix_me_server_id = ring.get_node(key)
    print(f"key={key},server_id={fix_me_server_id}")
    response = clients[fix_me_server_id].send(data_bytes)
    return response

# @cache('get')


def get(key, data_bytes):
    # if is_member(user_hash):

    # todo hash
    fix_me_server_id = ring.get_node(key)
    print(f"key={key},server_id={fix_me_server_id}")
    response = clients[fix_me_server_id].send(data_bytes)
    resStr = deserialize(response)
    return resStr
    # else:
    #     return None


# @cache('delete')
def delete(key, data_bytes):
    # if is_member(user_hash):

    # todo hash
    fix_me_server_id = ring.get_node(key)
    print(f"key={key},server_id={fix_me_server_id}")
    response = clients[fix_me_server_id].send(data_bytes)
    resStr = deserialize(response)
    return resStr


def process(udp_clients):
    global clients
    clients = udp_clients
    hash_codes = set()

    # PUT all users.
    print("begin to put users")
    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        response = put(key, u, data_bytes)
        response = str(response, encoding='utf-8')
        hash_codes.add(response)
        print(f"PUT response: {response}")
        # print(response)

    print(
        f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    # TODO: PART I
    # GET all users.
    print("begin to get users")
    for hc in hash_codes:
        data_bytes, key = serialize_GET(hc)
        response = get(key, data_bytes)
        # debug code, check response
        # resStr = deserialize(response)
        print(f"GET response: {response}")

    # DELETE all users.
    print("begin to delete users")
    for hc in hash_codes:
        data_bytes, key = serialize_DELETE(hc)
        response = delete(key, data_bytes)
        # debug code, check response

        print(f"DELETE response: {response}")

    # DELETE all users.
    print("begin to delete users2")
    for hc in hash_codes:
        data_bytes, key = serialize_DELETE(hc)
        response = delete(key, data_bytes)
        # debug code, check response
        # resStr = deserialize(response)
        print(f"DELETE response2: {response}")

     # GET all users again.
    print("begin to get users2")
    for hc in hash_codes:
        data_bytes, key = serialize_GET(hc)
        response = get(key, data_bytes)
        # debug code, check response
        # resStr = deserialize(response)
        print(f"GET response2: {response}")


if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    process(clients)

    time.sleep(10)
