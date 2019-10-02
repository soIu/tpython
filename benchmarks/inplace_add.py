print('begin test')
a = 1
b = 2
c = 0
def test():
	global a,b,c
	for i in range(1000000):
		c += a + b

test()
print(c)
print('ok')


