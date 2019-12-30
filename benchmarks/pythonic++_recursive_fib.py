## The Fibonacci Sequence ##

def main():
	print('enter main...')
	mymod.run_test(24)


with c++:
	def fib(int n) ->int:
		print("fib: ", n)
		if n == 0:
			return 0
		elif n == 1:
			return 1
		else:
			return fib(n-1) + fib(n-2)
	@module( mymod )
	def run_test(n):
		print('enter run_test...')
		auto a = fib( n )
		print(a)
		return None

import mymod
main()
