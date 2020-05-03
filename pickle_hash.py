import pickle
import hashlib


def serialize(object):
    return pickle.dumps(object)


def deserialize(object_bytes):
    return pickle.loads(object_bytes)


def hash_code_hex(data_bytes):
    hash_code = hashlib.md5(data_bytes)
    return hash_code.hexdigest()


def serialize_PUT(object):
    object_bytes = pickle.dumps(object)
    hash_code = hash_code_hex(object_bytes)
    envelope_bytes = pickle.dumps({
        'operation': 'PUT',
        'id': hash_code,
        'payload': object
    })
    return envelope_bytes, hash_code

def serialize_GET(id):
    envelope_bytes = pickle.dumps({
        'operation': 'GET',
        'id': id
    })
    return envelope_bytes, id

def serialize_DELETE(id):
    envelope_bytes = pickle.dumps({
        'operation': 'DELETE',
        'id': id
    })
    return envelope_bytes, id


def test():
    data_bytes, hash_code = serialize_PUT({ 'user': 'Foo' })
    print(f"Data Bytes={data_bytes}\nHash Code={hash_code}")

