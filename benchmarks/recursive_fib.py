## The Fibonacci Sequence ##

def main():
	print('enter main...')
	run_test()

def run_test():
	print('enter run_test...')
	a = fib( 24 )
	print(a)

def fib(n):
	print('fib: ', n)  ## crashes with signal 11 without this print!
	if n == 0:
		return 0
	elif n == 1:
		return 1
	else:
		return fib(n-1) + fib(n-2)

main()
