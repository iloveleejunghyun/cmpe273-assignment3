# 我需要修改名字
from lru_cache import lru_cache

# ？ 这个是干嘛的？
INVOKE_COUNT = 0

# 为什么参数是3？
# 我需要改变代码了。

count = 0
@lru_cache(3)
def fibonacci(n):
    # ？这里面的功能是什么？递归函数？
    if n < 2:
        # print(n, n)
        return n
    val = fibonacci(n-2) + fibonacci(n-1)
    global count
    count = count+1
    # print(count)
    # print(n, val)
    return val

# 为什么参数变成4了？
# ？参数和上面函数不同，会导致什么？
@lru_cache(4)
def get_data(key):
    global INVOKE_COUNT
    # 计数器加一了
    INVOKE_COUNT = INVOKE_COUNT + 1
    # 返回的是dict，id是键，值是组合键str
    return {'id': key, 'value': f'Foo Bar - {key}'}

# ？ 测试获取数据是什么意思？


def test_get_data(keys):
    for x in keys:
        # 遍历，获取数据，打印结果。x是数字，result是dict。
        result = get_data(x)
        print(result)
    print(f'Num of function calls:{len(keys)}')


if __name__ == '__main__':
    # 调用函数，传入6.多次递归。这对cache有什么影响？
    # 函数实现感觉有问题？不用decorator是对的。
    print(f'fibonacci(6)={fibonacci(6)}\n')

    # 传入10个数字的数组。有1234重复。调用总次数应该是6，因为有4个重复的。
    # 但是这里有问题了。我的decorator里面不能判断函数名字。或者说，也需要定制化？可以。
    test_get_data([1, 2, 3, 4, 1, 2, 3, 4, 5, 6])
    print(f'Num of cache misses:{INVOKE_COUNT}')
    assert INVOKE_COUNT == 6
