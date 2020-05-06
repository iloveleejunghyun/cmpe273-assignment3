from bloom_filter import BloomFilter

import sys
import socket
import time
import queue

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, deserialize, serialize_DELETE
from node_ring import NodeRing
from cache import lru_cache

BUFFER_SIZE = 1024


ring = NodeRing(nodes=[0, 1, 2, 3])
clients = []

# Bloom filter initialization
bf = BloomFilter()


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



def add_member(key):
    bf.add(key)


def is_member(key):
    return bf.__contains__(key)


@lru_cache
def put(key, user, data_bytes):
    add_member(key)
    print(f"add member {key} to bf")
    fix_me_server_id = ring.get_node(key)
    print(f"key={key},server_id={fix_me_server_id}")
    response = clients[fix_me_server_id].send(data_bytes)
    # response = deserialize(response)
    response = str(response, encoding='utf-8')
    return response


@lru_cache
def get(key, data_bytes):
    if is_member(key):
        print(f"{key} is a member")
        fix_me_server_id = ring.get_node(key)
        print(f"key={key},server_id={fix_me_server_id}")
        response = clients[fix_me_server_id].send(data_bytes)
        resStr = deserialize(response)
        return resStr
    else:
        print(f"{key} is not a member")
        return None


@lru_cache
def delete(key, data_bytes):
    if is_member(key):
        print(f"{key} is a member")
        fix_me_server_id = ring.get_node(key)
        print(f"key={key},server_id={fix_me_server_id}")
        response = clients[fix_me_server_id].send(data_bytes)
        resStr = deserialize(response)
        return resStr
    else:
        print(f"{key} is not a member")
        return 'success'


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
