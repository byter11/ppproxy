from cache import Cache, Schedule

c = Cache(Schedule.LRU, 3)
c.put("j", b"j")
c.put("k", b"k")
c.put("l", b"l")
print(c)

c.get('j')
print(c)

c.setschedule(Schedule.FIFO)
c.get('k')
print(c)