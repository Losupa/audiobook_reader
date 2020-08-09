from threading import Thread, Lock
import queue
import numpy as np


class Circle_Buffer(object):

	def __init__(self, capacity=500, growable=False, dtype="f8"):

		# Numpy datatype kind reference information
		# https://numpy.org/doc/stable/reference/generated/numpy.dtype.kind.html#numpy.dtype.kind
			
		
		self.cbuffer = np.empty(capacity, dtype)
		self.begin = 0
		self.end = -1
		self.size = 0
		self.capacity = capacity
		self.dtype = dtype
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
	def __init__(self, node_num=None, cb_capacity=200, cb_growable=True, cb_dtype="u4, U16"):
		"""
		Event queue for the event node
		with a parent class of a Circle_Buffer
		Default Datatype: unsigned 4 byte int, unicode 16 char string
		"""
		# Inherits from Parent class all varaibles
		# and functions, as well as calling its init function
		super().__init__(cb_capacity, cb_growable, cb_dtype)

		# Unique Node number that will be attached to all
		# events when published
		self.node_num = node_num

		# Event manager that will be a central bus
		# for events
		self.event_manager = Event_Manager()

		# Flag that signifies if the circular buffer is being modified
		# and thus unstable
		self.node_lock = Lock()

	def subscribe(self, event_manager):
		'''
		Subscribes to an event manager
		'''
		event_manager.lock.clear()
		self.event_manager = event_manager
		event_manager.add_node(self)
		event_manager.lock.set()

	def publish(self, event):
		# Perhaps change wait to check if lock is set
		# and if it is then add event to temporary queue
		# which will be added once lock is set
		self.event_manager.lock()
		self.event_manager.lock.clear()

		self.event_manager.push(self.node_num, event)
		self.event_manager.lock.set()

	def process(self):
		pass

class Event_Manager(Circle_Buffer):

	def __init__(self, node_num=None, cb_capacity=200, cb_growable=True, cb_dtype="u4, U16"):

		# Inherits from Parent class all varaibles
		# and functions, as well as calling its init function
		super().__init__(cb_capacity, cb_growable, cb_dtype)

		# List of nodes to be broadcasted to
		self.event_nodes = []

		# Flag that is True when events need to be broadcast
		# and false otherwise
		self.flag = False

		self.lock = Event()


	def add_node(self, event_node):
		self.event_nodes.append(event_node)

	def notify(self):

		for node in self.event_nodes:
			node.push(self.front())

		self.pop()

	def run(self):
		"""
		Main function that will be running all the time
		on the Event Manager and notifying when new events flag
		is set
		"""
		pass