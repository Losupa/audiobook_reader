import numpy as np
from threading import Thread, Event, Lock

class testNode(Thread):
	def __init__(self, group, target, name, args, kwargs, *, daemon):
		super().__init__(group, target, name, args, kwargs, *, daemon)

		self.arr = np.arange(10)

		self.masterNode = None

		

	def run(self):

		
		return super().run()

	def view(self, ind=0):
