def test():
	print('testing basic math ops')
	assert 1+1 == 2
	assert 10-1 == 9
	assert 10 / 2 == 5
	assert int(100.9) == 100

	print('testing bitwise ops')
	print(100 ^ 0xd008)
	assert 100 ^ 0xd008 == 53356
	
	print( 100 & 199 )
	assert (100 & 199) == 68
	
	## TODO fixme
	print('TODO fix `100 & 199 == 68`')
	assert 100 & 199 == 68

test()
