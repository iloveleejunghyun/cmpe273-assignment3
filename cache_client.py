import functools
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
    # if not is_member(user):
    #    add_member(user)
    # hash
    fix_me_server_id = ring.get_node(key)
    print(f"key={key},server_id={fix_me_server_id}")
    response = clients[fix_me_server_id].send(data_bytes)
    # response = deserialize(response)
    response = str(response, encoding='utf-8')
    return response


@lru_cache
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


@lru_cache
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
