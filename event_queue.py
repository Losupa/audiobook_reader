import threading
import queue
import numpy as np

class Circle_Buffer(object):

	def __init__(self, *args, **kwargs):

		# Default configuration for the cbuffer
		cbuffer_capacity = 500
		cbuffer_dtype = np.float64
		growable = False

		for key, value in kwargs.items():

			if (key == "capacity"):
				cbuffer_capacity = value

			# cbuffer_type is a tuple of strings,
			# with the strings being the name of the datatype you want
			# (int, float, string, bool)
			elif (key == "dtype"):
				cbuffer_dtype = value
			
			elif (key == "growable"):
				growable = value
			
			
		self.cbuffer = np.empty(cbuffer_capacity, cbuffer_dtype)
		self.begin = 0
		self.end = -1
		self.size = 0
		self.capacity = cbuffer_capacity
		self.dtype = cbuffer_dtype
		self.growable = growable

	def __len__(self):

		return self.size

	def at(self, index):
		try:
			return self.cbuffer[index]
		except:
			pass

	def front(self):
		return self.cbuffer[self.begin]
	
	def back(self):
		return self.cbuffer[self.end]

	def push(self, new_value):

		if (self.size >= self.capacity):
			if self.growable:
				self.grow()
			else:
				# Exception
				pass
		
		self.end = (self.begin + self.size) % self.capacity
		self.cbuffer[self.end] = new_value
		self.size += 1

		
	def pop(self):
		if (self.size > 0):
			self.begin = (self.begin + 1) % self.capacity
			self.size -= 1
		else:
			# Exception
			pass

	def grow(self):
		if (self.begin <= self.end):
			self.cbuffer = np.concatenate((self.cbuffer[self.begin : self.end + 1],
				np.empty(2 * self.capacity - self.size, dtype=self.dtype)))
		else:
			self.cbuffer = np.concatenate((self.cbuffer[self.begin :], self.cbuffer[self.end : self.begin],
				np.empty(2* self.capacity - self.size, dtype=self.dtype)))

		self.begin = 0
		self.end = self.begin + self.size - 1
		self.capacity *= 2

class Event_Node(Circle_Buffer):
	def __init__(self, *args, **kwargs):

		# Inherits from Parent class all varaibles
		# and functions, as well as calling its init function
		super().__init__(*args, **kwargs)

		self.event_manager = None

		self.event_queue = Circle_Buffer(capacity=200, growable=True, )

		for key, value in kwargs.items():
			if key == "event_manager":
				self.event_manager = value

	def view(self):

		return self.event_queue.front()

	def publish(self, event):
		self.event_bus.push(event)

class Event_Framework(object):

	def __init__(self):

		# Circle Buffer for events that need
		# to be broadcasted, due to the fact it is a buffer
		# you can technically view it asynchronously
		self.event_queue = Circle_Buffer(dtype="")

		# Nodes to be broadcasted to
		self.event_nodes = []

	def notify(self):

		#event =
		#for node in self.event_nodes:
		#	pass
		pass
