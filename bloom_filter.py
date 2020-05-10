# coding=utf-8
# pylint: disable=superfluous-parens,redefined-variable-type
# superfluous-parens: Sometimes extra parens are more clear

"""Bloom Filter: Probabilistic set membership testing for large sets"""

# Shamelessly borrowed (under MIT license) from http://code.activestate.com/recipes/577686-bloom-filter/
# About Bloom Filters: http://en.wikipedia.org/wiki/Bloom_filter

# Tweaked by Daniel Richard Stromberg, mostly to:
# 1) Give it a little nicer __init__ parameters.
# 2) Improve the hash functions to get a much lower rate of false positives.
# 3) Give it a selection of backends.
# 4) Make it pass pylint.

from __future__ import division
import os
# mport sys
import math
import array
import random

try:
    import mmap as mmap_mod
except ImportError:
    # Jython lacks mmap()
    HAVE_MMAP = False
else:
    HAVE_MMAP = True

# mport bufsock
# mport hashlib
# mport numbers

import python2x3

# In the literature:
# k is the number of probes - we call this num_probes_k
# m is the number of bits in the filter - we call this num_bits_m
# n is the ideal number of elements to eventually be stored in the filter - we call this ideal_num_elements_n
# p is the desired error rate when full - we call this error_rate_p


def my_range(num_values):
    """Generate numbers from 0..num_values-1"""

    value = 0
    while value < num_values:
        yield value
        value += 1


class Array_backend(object):
    """Backend storage for our "array of bits" using a python array of integers"""

    # Note that this has now been split out into a bits_mod for the benefit of other projects.
    effs = 2 ** 32 - 1

    def __init__(self, num_bits):
        self.num_bits = num_bits
        self.num_words = (self.num_bits + 31) // 32
        self.array_ = array.array('L', [0]) * self.num_words

    def is_set(self, bitno):
        """Return true iff bit number bitno is set"""
        wordno, bit_within_wordno = divmod(bitno, 32)
        mask = 1 << bit_within_wordno
        return self.array_[wordno] & mask

    def set(self, bitno):
        """set bit number bitno to true"""
        wordno, bit_within_wordno = divmod(bitno, 32)
        mask = 1 << bit_within_wordno
        self.array_[wordno] |= mask

    def clear(self, bitno):
        """clear bit number bitno - set it to false"""
        wordno, bit_within_wordno = divmod(bitno, 32)
        mask = Array_backend.effs - (1 << bit_within_wordno)
        self.array_[wordno] &= mask

    # It'd be nice to do __iand__ and __ior__ in a base class, but that'd be Much slower

    def __iand__(self, other):
        assert self.num_bits == other.num_bits

        for wordno in my_range(self.num_words):
            self.array_[wordno] &= other.array_[wordno]

        return self

    def __ior__(self, other):
        assert self.num_bits == other.num_bits

        for wordno in my_range(self.num_words):
            self.array_[wordno] |= other.array_[wordno]

        return self

    def close(self):
        """Noop for compatibility with the file+seek backend"""
        pass


def get_bitno_seed_rnd(bloom_filter, key):
    """Apply num_probes_k hash functions to key.  Generate the array index and bitmask corresponding to each result"""

    # We're using key as a seed to a pseudorandom number generator
    hasher = random.Random(key).randrange
    for dummy in range(bloom_filter.num_probes_k):
        bitno = hasher(bloom_filter.num_bits_m)
        yield bitno % bloom_filter.num_bits_m


MERSENNES1 = [2 ** x - 1 for x in [17, 31, 127]]
MERSENNES2 = [2 ** x - 1 for x in [19, 67, 257]]


def simple_hash(int_list, prime1, prime2, prime3):
    """Compute a hash value from a list of integers and 3 primes"""
    result = 0
    for integer in int_list:
        result += ((result + integer + prime1) * prime2) % prime3
    return result


def hash1(int_list):
    """Basic hash function #1"""
    return simple_hash(int_list, MERSENNES1[0], MERSENNES1[1], MERSENNES1[2])


def hash2(int_list):
    """Basic hash function #2"""
    return simple_hash(int_list, MERSENNES2[0], MERSENNES2[1], MERSENNES2[2])


def get_bitno_lin_comb(bloom_filter, key):
    """Apply num_probes_k hash functions to key.  Generate the array index and bitmask corresponding to each result"""

    # This one assumes key is either bytes or str (or other list of integers)

    # I'd love to check for long too, but that doesn't exist in 3.2, and 2.5 doesn't have the numbers.Integral base type
    if hasattr(key, '__divmod__'):
        int_list = []
        temp = key
        while temp:
            quotient, remainder = divmod(temp, 256)
            int_list.append(remainder)
            temp = quotient
    elif hasattr(key[0], '__divmod__'):
        int_list = key
    elif isinstance(key[0], str):
        int_list = [ord(char) for char in key]
    else:
        raise TypeError('Sorry, I do not know how to hash this type')

    hash_value1 = hash1(int_list)
    hash_value2 = hash2(int_list)

    # We're using linear combinations of hash_value1 and hash_value2 to obtain num_probes_k hash functions
    for probeno in range(1, bloom_filter.num_probes_k + 1):
        bit_index = hash_value1 + probeno * hash_value2
        yield bit_index % bloom_filter.num_bits_m


def try_unlink(filename):
    """unlink a file.  Don't complain if it's not there"""
    try:
        os.unlink(filename)
    except OSError:
        pass
    return


class BloomFilter(object):
    """Probabilistic set membership testing for large sets"""

    def __init__(self,
                 max_elements=10000,
                 error_rate=0.1,
                 probe_bitnoer=get_bitno_lin_comb,
                 filename=None,
                 start_fresh=False):
        # pylint: disable=R0913
        # R0913: We want a few arguments
        if max_elements <= 0:
            raise ValueError('ideal_num_elements_n must be > 0')
        if not (0 < error_rate < 1):
            raise ValueError('error_rate_p must be between 0 and 1 exclusive')

        self.error_rate_p = error_rate
        # With fewer elements, we should do very well.  With more elements, our error rate "guarantee"
        # drops rapidly.
        self.ideal_num_elements_n = max_elements

        numerator = -1 * self.ideal_num_elements_n * \
            math.log(self.error_rate_p)
        denominator = math.log(2) ** 2
        real_num_bits_m = numerator / denominator
        self.num_bits_m = int(math.ceil(real_num_bits_m))

        self.backend = Array_backend(self.num_bits_m)

        # AKA num_offsetters
        # Verified against http://en.wikipedia.org/wiki/Bloom_filter#Probability_of_false_positives
        real_num_probes_k = (
            self.num_bits_m / self.ideal_num_elements_n) * math.log(2)
        self.num_probes_k = int(math.ceil(real_num_probes_k))
        self.probe_bitnoer = probe_bitnoer

    def __repr__(self):
        return 'BloomFilter(ideal_num_elements_n=%d, error_rate_p=%f, num_bits_m=%d)' % (
            self.ideal_num_elements_n,
            self.error_rate_p,
            self.num_bits_m,
        )

    def add(self, key):
        """Add an element to the filter"""
        for bitno in self.probe_bitnoer(self, key):
            self.backend.set(bitno)

    def __iadd__(self, key):
        self.add(key)
        return self

    def __contains__(self, key):
        for bitno in self.probe_bitnoer(self, key):
            if not self.backend.is_set(bitno):
                return False
        return True

    def is_member(self, key):
        return self.__contains__(key)


def test_yuan():
    bf = BloomFilter()
    key1 = 'key1'
    key2 = 'key2'

    print(bf.__contains__('key1'))
    bf.add('key1')
    print(bf.__contains__('key1'))

    print(bf.__contains__('key2'))
    bf.add('key2')
    print(bf.__contains__('key2'))


test_yuan()
