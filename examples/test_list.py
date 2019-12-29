def test():
	u = [100, 200]
	print(u)
	print('len: ', len(u))
	a = []
	print("append func:", a.append)
	print("insert func:", a.insert)
	print("pop func:", a.pop)
	print("extend func:", a.extend)
	a.append(1)
	print(a)
	a.append(2)
	print(a)
	#b = a[:]  ## TODO support slice copy
	#print(b)
	print('testing copy vec list')
	c = list(a)
	print(c)
	print('testing index vec list')
	print( c[0] )
	print( c[-1] )
	print('testing vec list multiply by number')
	print( c * 4 )
	print('testing vec list extend')
	print('extend func: ', c.extend)
	c.extend([99,100])
	print(c)
	print('--------------------------')
	x = ['a', 'b', 'c']
	print(x)
	print('len: ', len(x))
	print(x[0])
	print(x[-1])
	print(x * 4 )
	x.extend([99,100])
	print(x)
	
	print('testing 2d list')
	d = []
	d.append(a)
	d.append(c)
	print(d)

	## TODO support list comprehensions
	print('testing list comp')
	e = [i for i in range(10)]
	print(e)	
	

test()
