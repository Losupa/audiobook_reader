from threading import Thread, Lock, Event, Condition
import queue
import numpy as np
from time import sleep


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

	def __repr__(self):
	 return self.cbuffer.__repr__()

	def __len__(self):

		return self.size

	def __getitem__(self, key):
		if isinstance(key, slice):
			start, stop, step = key.indices(len(self))
			return self.cbuffer[start:stop:step]
		elif isinstance(key, int):
			return self.cbuffer[key]
		else:
			raise TypeError("Invalid argument type: {}".format(type(key)))
	
	def __setitem__(self, key, value):
		if isinstance(key, slice):
			start, stop, step = key.indices(len(self))
			self.cbuffer[start:stop:step] = value
		elif isinstance(key, int):
			self.cbuffer[key] = value
		else:
			raise TypeError("Invalid argument type: {}".format(type(key)))

	def front(self):
		return self.cbuffer[self.begin]
	
	def back(self):
		return self.cbuffer[self.end]

	def all(self):
		if self.size == 0:
			return np.array([])
		elif self.begin > self.end:
			return np.concatenate(self.cbuffer[:self.end], self.cbuffer[self.begin:])
		return self.cbuffer[self.begin:self.end]

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
		with utilizing 2 Circle_Buffers-one for incoming events
		and one for outgoing events
		Default Datatype: unsigned 4 byte int, unicode 16 char string
		"""
		# Inherits from Parent class all varaibles
		# and functions, as well as calling its init function
		super().__init__(cb_capacity, cb_growable, cb_dtype)

		# Unique Node number relative to event manager
		# Event Manager's Node Num is 0
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
		self.node_num = event_manager.add_node(self)
		event_manager.lock.set()

	def publish(self, event):
		# Perhaps change wait to check if lock is set
		# and if it is then add event to temporary queue
		# which will be added once lock is set

		self.event_manager.push_event(self.node_num, event)

	def process(self):
		pass

class Event_Manager(Circle_Buffer):

	def __init__(self, node_num=None, cb_capacity=200, cb_growable=True, cb_dtype="u4, U16"):

		# Inherits from Parent class all varaibles
		# and functions, as well as calling its init function
		super().__init__(cb_capacity, cb_growable, cb_dtype)

		# List of nodes to be broadcasted to
		self.event_nodes = []
		# Event Manager's default node num is 0
		self.node_num = 0


		# Flag that is True when events need to be broadcast
		# and false otherwise
		self.flag = Condition(Lock())
		self.flag.acquire()

		self.flag_lock = Event()

		# Main lock for circle_buffer
		self.cb_lock = Event()

		# Lock for list of nodes
		self.nodes_lock = Event()



	def add_node(self, event_node):
		self.nodes_lock.clear()
		self.event_nodes.append(event_node)
		self.nodes_lock.set()
		return len(event_nodes)

	def push_event(self, event):
		"""
		Pushes event to Event Manager CB
		and sets flag to True if not already
		"""

		self.cb_lock.wait()
		self.cb_lock.clear()
		self.push(self.node_num, event)
		self.cb_lock.set()
		
		self.flag_lock.wait()
		self.flag_lock.clear()
		
		if self.flag.locked():
			self.flag.release()

		self.flag_lock.set()
		


	def pop_event(self):
		self.cb_lock.wait()
		self.cb_lock.clear()
		self.pop()

		if self.size == 0:
			self.flag.acquire(False)

		self.cb_lock.set()


	def notify(self):

		while not self.flag.locked():
			
			# Does not notify if list of nodes is being modified
			self.nodes_lock.wait()

			for node in self.event_nodes:
				node.cb_lock.wait()
				node.cb_lock.clear()

				node.push(self.front())
				
				node.cb_lock.set()

			self.pop_event()

	def run(self):
		"""
		Main function that will be running all the time
		on the Event Manager and notifying when new events flag
		is set
		"""
		while (True):
			
			self.flag.wait()
			self.notify()
