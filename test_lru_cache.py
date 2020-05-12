from lru_cache import lru_cache

INVOKE_COUNT = 0

@lru_cache(3)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-2) + fibonacci(n-1)

@lru_cache(4)
def get_data(key):
    global INVOKE_COUNT
    INVOKE_COUNT = INVOKE_COUNT + 1
    return { 'id': key, 'value': f'Foo Bar - {key}' }

def test_get_data(keys):
    for x in keys:
        result = get_data(x)
        print(result)
    print(f'Num of function calls:{len(keys)}')

  
if __name__=='__main__':
    print(f'fibonacci(6)={fibonacci(6)}\n')
    test_get_data([1, 2, 3, 4, 1, 2, 3, 4, 5, 6])
    print(f'Num of cache misses:{INVOKE_COUNT}')
    assert INVOKE_COUNT == 6
 