# cache and bloom filter based on midterm

What are the best k hashes and m bits values to store one million n keys (E.g. e52f43cd2c23bb2e6296153748382764) suppose we use the same MD5 hash key from pickle_hash.py and explain why?  

Consider p = 0.05, then  

m =(-1 * n * math.log(p))/ (math.log(2) ** 2)= 6235225  
k = (m / n) * math.log(2)= 5

m,k are calculated by python  


## Installation
	pip install mmh3
## Example:

In cache_client.py, you can see the process function is modified to execute PUT, GET, DELETE, DELETE, and GET method to verify the cache and bloom filter function.




# LRU Cache and Bloom Filter

The assignment 3 is based on our simple [distributed cache](https://github.com/sithu/cmpe273-spring20/tree/master/midterm) where you have implmented the GET and PUT operations.

## 1. DELETE operation

You will be adding the DELETE operation to delete entires from the distributed cache.

_Request_

```json
{ 
    'operation': 'DELETE',
    'id': 'hash_code_of_the_object',
}
```

_Response_

```json
{
    'success'
}
```

## 2. LRU Cache

In order to reduce unnecessary network calls to the servers, you will be adding LRU cache on client side. On each GET, PUT, and DELETE call, you will be checking against data from a local cache.

Implement LRU cache as Python decorator and you can pass cache size as argument.

```python
@lru_cache(5)
def get(...):
    ...
    return ...
    
@lru_cache(5)
def put(...):
    ...
    return ...

@lru_cache(5)
def delete(...):
    ...
    return ...

```

@lru_cache is your implementation as a decorator function and do NOT use any existing LRU libraries.

## 3. Bloom Filter

Finally, you will be implementing a bloom filter so that we can validate any key lookup without hitting the servers. The bloom filter will have two operations:

### Add

This add() function handles adding new key to the membership set.

### Is_member

This is_member() function checks whether a given key is in the membership or not.

On the client side, the GET and DELETE will invoke is_member(key) function first prior to calling the servers while the PUT and DELETE will call add(key) function to update the membership.

Answer the following question:

* What are the best _k_ hashes and _m_ bits values to store one million _n_ keys (E.g. e52f43cd2c23bb2e6296153748382764) suppose we use the same MD5 hash key from [pickle_hash.py](https://github.com/sithu/cmpe273-spring20/blob/master/midterm/pickle_hash.py#L14) and explain why?

```python
@lru_cache(5)
def get(key):
    if bloomfilter.is_member(key):
        return udp_client.get(key)
    else:
        return None
        
@lru_cache(5)
def put(key, value):
    bloomfilter.add(key)
    return udp_client.put(key, value)

@lru_cache(5)
def delete(key):
    if bloomfilter.is_member(key):
        return udp_client.delete(key)
    else:
        return None

```





