import unittest

import numpy as np

from event_framework import Circle_Buffer

from threading import Thread
from time import sleep, time
from datetime import datetime, timedelta

class CircleBufferCase(unittest.TestCase):
	
	def test_basic_init(self):
		cb = Circle_Buffer()
		
		# Checks default init settings
		self.assertEqual(len(cb), 0)
		self.assertEqual(cb.capacity, 500)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, -1)
		self.assertEqual(cb.growable, False)
		self.assertEqual(cb.dtype, 'f8')


		cb.push(5)
		self.assertEqual(len(cb), 1)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 0)
		self.assertAlmostEqual(cb.front(), 5)
		self.assertAlmostEqual(cb.back(), 5)
		self.assertAlmostEqual(cb[0], 5)

		cb.push(10)
		self.assertEqual(len(cb), 2)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 1)
		self.assertAlmostEqual(cb.front(), 5)
		self.assertAlmostEqual(cb.back(), 10)
		self.assertAlmostEqual(cb[1], 10)


		cb.pop()
		self.assertEqual(len(cb), 1)
		self.assertEqual(cb.begin, 1)
		self.assertEqual(cb.end, 1)
		self.assertAlmostEqual(cb.front(), 10)
		self.assertAlmostEqual(cb.back(), 10)

		cb.pop()
		self.assertEqual(len(cb), 0)
		self.assertEqual(cb.begin, 2)
		self.assertEqual(cb.end, 1)

		cb[0] = 15
		self.assertAlmostEqual(cb[0], 15)


	def test_different_cap(self):
		cb = Circle_Buffer(capacity=2)

		self.assertEqual(cb.capacity, 2)
		self.assertEqual(len(cb), 0)

		cb.push(5)
		self.assertEqual(len(cb), 1)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 0)
		self.assertAlmostEqual(cb.front(), 5)
		self.assertAlmostEqual(cb.back(), 5)

		cb.push(10)
		self.assertEqual(len(cb), 2)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 1)
		self.assertAlmostEqual(cb.front(), 5)
		self.assertAlmostEqual(cb.back(), 10)

		cb.pop()
		self.assertEqual(len(cb), 1)
		self.assertEqual(cb.begin, 1)
		self.assertEqual(cb.end, 1)
		self.assertAlmostEqual(cb.front(), 10)
		self.assertAlmostEqual(cb.back(), 10)

		cb.push(15)
		self.assertEqual(len(cb), 2)
		self.assertEqual(cb.begin, 1)
		self.assertEqual(cb.end, 0)
		self.assertAlmostEqual(cb.front(), 10)
		self.assertAlmostEqual(cb.back(), 15)

		cb.pop()
		self.assertEqual(len(cb), 1)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 0)
		self.assertAlmostEqual(cb.front(), 15)
		self.assertAlmostEqual(cb.back(), 15)

		cb.pop()
		self.assertEqual(len(cb), 0)
		self.assertEqual(cb.begin, 1)
		self.assertEqual(cb.end, 0)


	def test_different_dtype(self):
		
		cb = Circle_Buffer(capacity=3, dtype="i8, U25, f8")
		self.assertEqual(len(cb), 0)
		self.assertEqual(cb.capacity, 3)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, -1)
		self.assertEqual(cb.growable, False)
		self.assertEqual(cb.dtype, "i8, U25, f8")

		cb.push((2, "hello", 2.5))
		self.assertEqual(len(cb), 1)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 0)
		test_val = cb.front()
		self.assertEqual(test_val[0], 2)
		self.assertEqual(test_val[1], "hello")
		self.assertAlmostEqual(test_val[2], 2.5)
		test_val = cb.back()
		self.assertEqual(test_val[0], 2)
		self.assertEqual(test_val[1], "hello")
		self.assertAlmostEqual(test_val[2], 2.5)

	def test_growable(self):

		cb = Circle_Buffer(capacity=4, growable=True)
		
		self.assertEqual(len(cb), 0)
		self.assertEqual(cb.capacity, 4)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, -1)
		self.assertEqual(cb.growable, True)
		self.assertEqual(cb.dtype, "f8")

		cb.push(3)
		cb.push(7)
		cb.push(11)
		cb.push(17)

		self.assertEqual(len(cb), 4)
		self.assertEqual(cb.capacity, 4)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 3)

		self.assertAlmostEqual(cb.front(), 3)
		self.assertAlmostEqual(cb.back(), 17)

		cb.push(5)

		self.assertEqual(len(cb), 5)
		self.assertEqual(cb.capacity, 8)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 4)
		self.assertAlmostEqual(cb.front(), 3)
		self.assertAlmostEqual(cb.back(), 5)

		cb = Circle_Buffer(capacity=4, growable=True)

		cb.push(3)
		cb.push(7)
		cb.push(11)
		cb.push(17)

		cb.pop()
		cb.push(5)

		self.assertEqual(len(cb), 4)
		self.assertEqual(cb.capacity, 4)
		self.assertEqual(cb.begin, 1)
		self.assertEqual(cb.end, 0)
		self.assertAlmostEqual(cb.front(), 7.0)
		self.assertAlmostEqual(cb.back(), 5.0)

		cb.push(19)

		self.assertEqual(len(cb), 5)
		self.assertEqual(cb.capacity, 8)
		self.assertEqual(cb.begin, 0)
		self.assertEqual(cb.end, 4)
		self.assertAlmostEqual(cb.front(), 7.0)
		self.assertAlmostEqual(cb.back(), 19.0)

		cb.pop()
		self.assertAlmostEqual(cb.front(), 11)

	def test_cb_push_multithreading(self):

		'''
		Basic test on whether or not circle buffer push is thread safe as long
		as circle buffer does not become too full
		'''
		def push_to_cb(self, cb):
			for i in range(10, 20):
				cb.push(100)
				#print("T1: {}".format(cb[0:len(cb)]))

		def modify_cb(self, cb):
			i = 0
			for i in range(10):
				cb[i] = i
				#print("T2: {}".format(cb[0:len(cb)]))
		
		cb = Circle_Buffer()

		cb.push(5)
		cb.push(6)
		cb.push(7)
		cb.push(8)
		cb.push(9)

		t1 = Thread(target=push_to_cb, args=(self, cb))
		t2 = Thread(target=modify_cb, args=(self, cb))
		t1.start()
		t2.start()
		t1.join()
		t2.join()


if __name__ == '__main__':
	unittest.main(verbosity=2)
