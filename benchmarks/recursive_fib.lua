-- The Fibonacci Sequence ##

function fib(n)
	if n < 3 then
		return 1
	else
		return fib(n-1) + fib(n-2)
	end
end

io.write('enter main...\n')

a = 0
for n=1, 32 do
	a = fib( 32 )
end
io.write(a, "\n")


