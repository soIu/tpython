## The Fibonacci Sequence ##

with c++:
	def fib(int n) ->int:
		if n == 0:
			return 0
		elif n == 1:
			return 1
		else:
			return fib(n-1) + fib(n-2)
	@module( my_cpp_module )
	def run_recursive_fib(n):
		print('enter run_test...')
		auto a = fib( n )
		print(a)
		return None

import my_cpp_module

def main():
	print('enter main...')
	my_cpp_module.run_recursive_fib(32)

main()
