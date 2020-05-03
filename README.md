# Midterm Exam Coding Questions

You will be building a distributed cache solution using UDP as transport protocol. Here is how the caching protocol works:

# PART I (15 points)

## PUT

PUT operation allows you to save any Python data type in a remote cache server.

### Request

```python
{ 
    'operation': 'PUT',
    'id': 'hash_code_of_the_object',
    'payload': 'any_object_that_you_want_to_cache_in_server' 
}
```

### Response

```python
{ 
    'hash_code_of_the_object'
}
```

## GET

GET operation allows you to retrieve any existing data stored in the remote cache server.

### Request

```python
{ 
    'operation': 'GET',
    'id': 'hash_code_of_the_object'
}
```

### Response

```python
{ 
    'object_in_bytes'
}
```

# Part I

The baseline code handles PUT operation and you need to implment GET operation according the above specification.

To run the baseline code (server side):

```
python3 cache_server.py 0
Cache Server[0] started at 127.0.0.1:4000
```

The last argument is the server index defined in _server_config.py_ .


To run the client code,

```
python3 cache_client.py
```

_Output_

```
Connecting to server at 127.0.0.1:4000
b'd0df71363130955e493c24ac0d296a75'
Connecting to server at 127.0.0.1:4000
b'1c84c3d6dec3775654c4573ca4df1064'
Connecting to server at 127.0.0.1:4000
b'e52f43cd2c23bb2e6296153748382764'
Connecting to server at 127.0.0.1:4000
b'9aa0c932fb8eba9a72a6ae60064a0507'
Connecting to server at 127.0.0.1:4000
b'6aaae4a8f8468ef61e78b4ced80fa140'
Connecting to server at 127.0.0.1:4000
b'd0df71363130955e493c24ac0d296a75'
Number of Users=6
Number of Users Cached=5
b'e52f43cd2c23bb2e6296153748382764'
Connecting to server at 127.0.0.1:4000
b'FIX_ME'
b'9aa0c932fb8eba9a72a6ae60064a0507'
Connecting to server at 127.0.0.1:4000
b'FIX_ME'
b'6aaae4a8f8468ef61e78b4ced80fa140'
Connecting to server at 127.0.0.1:4000
b'FIX_ME'
b'd0df71363130955e493c24ac0d296a75'
Connecting to server at 127.0.0.1:4000
b'FIX_ME'
b'1c84c3d6dec3775654c4573ca4df1064'
Connecting to server at 127.0.0.1:4000
b'FIX_ME'
```

Your job is to implement GET operation so that the GET response will have bytes data like this instead of FIX_ME:

```
b'\x80\x03}q\x00(X\t\x00\x00\x00operationq\x01X\x03\x00\x00\x00PUTq\x02X\x02\x00\x00\x00idq\x03X \x00\x00\x009ad5794ec94345c4873c4e591788743aq\x04X\x07\x00\x00\x00payloadq\x05}q\x06X\x04\x00\x00\x00userq\x07X\x03\x00\x00\x00Fooq\x08su.'
```

# PART II (15 points)

The current solution only talks to a single server (index 0). You will be splitting (sharding) data into all four servers listed in server_config.py.

Data sharding via Naive hashing is implemented in node_ring.py. You must use the def get_node(self, key_hex) function from the NodeRing() class to shard all users data into four nodes.

### FROM

All users go to Server index 0.

### TO

All users go to Servers index 0, 1, 2, and 3.

The given node_ring.py can handle key lookup like this:

```
python3 node_ring.py 
{'host': '127.0.0.1', 'port': 4002}
{'host': '127.0.0.1', 'port': 4000}
```