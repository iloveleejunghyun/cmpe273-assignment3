from bloom_filter import BloomFilter 
from random import shuffle 

NUM_KEYS = 20 
FALSE_POSITIVE_PROBABILITY = 0.05

def test_bloom_filter():
    bloomfilter = BloomFilter(NUM_KEYS, FALSE_POSITIVE_PROBABILITY) 
    word_present = ['abound','abounds','abundance','abundant','accessable', 
                    'bloom','blossom','bolster','bonny','bonus','bonuses', 
                    'coherent','cohesive','colorful','comely','comfort', 
                    'gems','generosity','generous','generously','genial'] 
    
    word_absent = ['facebook','twitter'] 
    
    for item in word_present: 
        bloomfilter.add(item) 
    
    test_words = word_present[:10] + word_absent 
    shuffle(test_words) 
    for word in test_words: 
        if bloomfilter.is_member(word): 
            if word in word_absent: 
                print(f"'{word}' is a false positive!") 
            else: 
                print(f"'{word}' is probably present!")
        else: 
            print(f"'{word}' is definitely not present!") 


if __name__=='__main__':
    test_bloom_filter()