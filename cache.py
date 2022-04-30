from enum import Enum
import os

class Schedule(Enum):
	LRU = 'lru'
	FIFO = 'fifo'

class Cache:
	def __init__(self, schedule : Schedule, size=10):
		self.cache = {}
		self.size = size
		self.setschedule(schedule)
		if not os.path.exists('cache'):
			os.makedirs('cache')

	def setschedule(self, schedule):
		if schedule not in Schedule:
			raise ValueError("Invalid Scheduling algorithm", schedule)
		self.schedule = schedule
	
	def get(self, key):
		if self.schedule == Schedule.FIFO: return self._getfifo(key)
		if self.schedule == Schedule.LRU: return self._getlru(key)
	
	def put(self, key, value):
		if self.cache.get(key):
			self.cache.pop(key)
			self.cache[key] = key
			return
			
		if len(self.cache.keys()) >= self.size:
			self.cache.pop(list(self.cache)[0])

		with open(f'cache/{key}.cache', 'wb') as f:
			f.write(value)
		self.cache[key] = key

	def _getfifo(self, key):
		if self.cache.get(key):
			return self._readfile(key)
					
		return False
	
	def _getlru(self, key):
		if self.cache.get(key):
			self.cache.pop(key)
			self.cache[key] = key
		else: return False

		return self._readfile(key)

	def __repr__(self):
		return ' | '.join(self.cache.keys())

	def _readfile(self, key):
		file = f'cache/{key}.cache'
		if not os.path.exists(file): return False
		with open(f'cache/{key}.cache', 'rb') as f:
			return f.read()