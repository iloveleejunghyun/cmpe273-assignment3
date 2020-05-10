# ？名字要取这个
from bloom_filter import BloomFilter
from random import shuffle

NUM_KEYS = 20
# ？错误的判断为真。干啥用的？
FALSE_POSITIVE_PROBABILITY = 0.05


def test_bloom_filter():
    # 两个参数。键的数量，FP的概率。
    # err_rate和FP是不是相等的呀？
    bloomfilter = BloomFilter(NUM_KEYS, FALSE_POSITIVE_PROBABILITY)
    # 这些是key吗？是的
    word_present = ['abound', 'abounds', 'abundance', 'abundant', 'accessable',
                    'bloom', 'blossom', 'bolster', 'bonny', 'bonus', 'bonuses',
                    'coherent', 'cohesive', 'colorful', 'comely', 'comfort',
                    'gems', 'generosity', 'generous', 'generously', 'genial']

    # 测试的没有key？是的
    word_absent = ['facebook', 'twitter']

    # 全部加到bf里面去
    for item in word_present:
        bloomfilter.add(item)

    # 取前10个元素的数组，加上缺失的两个元素素组。形成测试数组。
    test_words = word_present[:10] + word_absent

    #  shuffle是打乱的意思吗？是的，打乱顺序
    shuffle(test_words)

    # 遍历
    for word in test_words:

        if bloomfilter.is_member(word):
            # 如果是存在的，如果这个应该不存在，则打印FP
            if word in word_absent:
                print(f"'{word}' is a false positive!")
            # 否则打印可能存在，窝草。
            else:
                print(f"'{word}' is probably present!")
        else:
            # 如果不存在，则打印出不存在。
            print(f"'{word}' is definitely not present!")

    # ？我们打印出来的结果，能和prof一样吗？我感觉不一定啊。bf的算法都不一定相同。好像有指定。需求上，看看。
    # ？ 计算位数组的大小是干嘛？ 穿进去的不是位数组大小？ 好吧，的确不是。那个是key的数量。
    # ？ 老师的意思是使用mmh3进行hash运算？ 那么要进行几次？用哪几个hash？


if __name__ == '__main__':
    test_bloom_filter()
