print('begin test')
a = 1
b = 2
c = 0
function test()
	for i=1,1000000 do
		c = c + a + b
	end
end

test()
print(c)
print('ok')

