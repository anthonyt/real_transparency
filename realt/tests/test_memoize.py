import collections
import unittest

import realt

class TestMemoize(unittest.TestCase):
    def test_memoize(self):
        calls = collections.Counter()
        @realt.memoize
        def dummy_func():
            calls['dummy_func'] += 1
            return 'Called %d times' % (calls['dummy_func'],)

        result1 = dummy_func()
        result2 = dummy_func()
        self.assertEqual(result1, 'Called 1 times')
        self.assertEqual(result2, 'Called 1 times')
        self.assertEqual(calls['dummy_func'], 1)

    def test_memoize_reset(self):
        calls = collections.Counter()
        @realt.memoize
        def dummy_func():
            calls['dummy_func'] += 1
            return 'Called %d times' % (calls['dummy_func'],)

        result1 = dummy_func()
        dummy_func.clear_cache()
        result2 = dummy_func()
        self.assertEqual(result1, 'Called 1 times')
        self.assertEqual(result2, 'Called 2 times')
        self.assertEqual(calls['dummy_func'], 2)

    def test_memoize_args(self):
        calls = collections.Counter()
        @realt.memoize
        def dummy_func(a, b):
            calls['dummy_func'] += 1
            return 'Called %d times' % (calls['dummy_func'],)

        result1 = dummy_func('a', 'b')
        result2 = dummy_func('a', 'b')
        result3 = dummy_func('a', '_')
        self.assertEqual(result1, 'Called 1 times')
        self.assertEqual(result2, 'Called 1 times')
        self.assertEqual(result3, 'Called 2 times')
        self.assertEqual(calls['dummy_func'], 2)

    def test_memoize_kwargs(self):
        calls = collections.Counter()
        @realt.memoize
        def dummy_func(a, b):
            calls['dummy_func'] += 1
            return 'Called %d times' % (calls['dummy_func'],)

        result1 = dummy_func(a='a', b='b')
        result2 = dummy_func(b='b', a='a')
        result3 = dummy_func(a='a', b='_')
        self.assertEqual(result1, 'Called 1 times')
        self.assertEqual(result2, 'Called 1 times')
        self.assertEqual(result3, 'Called 2 times')
        self.assertEqual(calls['dummy_func'], 2)

    def test_memoize_args_kwargs(self):
        calls = collections.Counter()
        @realt.memoize
        def dummy_func(a, b):
            calls['dummy_func'] += 1
            return 'Called %d times' % (calls['dummy_func'],)

        result1 = dummy_func('a', b='b')
        result2 = dummy_func('a', b='b')
        result3 = dummy_func('a', b='_')
        self.assertEqual(result1, 'Called 1 times')
        self.assertEqual(result2, 'Called 1 times')
        self.assertEqual(result3, 'Called 2 times')
        self.assertEqual(calls['dummy_func'], 2)

    def test_memoize_conflicting_args_kwargs(self):
        calls = collections.Counter()
        @realt.memoize
        def dummy_func(a, b):
            calls['dummy_func'] += 1
            return 'Called %d times' % (calls['dummy_func'],)

        result1 = dummy_func('a', 'b')
        result2 = dummy_func(a='a', b='b')
        result3 = dummy_func('a', b='b')
        self.assertEqual(result1, 'Called 1 times')
        self.assertEqual(result2, 'Called 2 times')
        self.assertEqual(result3, 'Called 3 times')
        self.assertEqual(calls['dummy_func'], 3)
