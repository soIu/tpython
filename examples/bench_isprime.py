import threading

def is_prime(n):
	hits = 0
	for x in range(2, n):
		for y in range(2, n):
			if x*y == n:
				hits += 1
				if hits > 1:
					return False
	return True
		
def calc_primes(start, end):
	primes = []
	for i in range(start, end):
		if is_prime(i):
			primes.append(i)
	print( primes )


class thread(threading.Thread):
	def __init__(self, start, end):
		threading.Thread.__init__(self)
		self._start = start
		self._end = end
	def run(self):
		calc_primes(self._start, self._end)

t1 = thread(0, 620)
t2 = thread(621, 800)
t1.start()
t2.start()
t1.join()
t2.join()