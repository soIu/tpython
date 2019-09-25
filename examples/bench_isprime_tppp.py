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


with thread:
	calc_primes(0, 620)

with thread:
	calc_primes(621, 800)


