print( ['X', 'Y', 'Z'] )

s = 'x y z'
print( s.split(' ') )

m = '''line1
line2
line3'''
print( m.splitlines() )

if not s.startswith('x'):
	raise RuntimeError('string.startswith test failed')
else:
	print('startswith test OK')

if not s.endswith('z'):
	raise RuntimeError('string.endswith test failed')
else:
	print('endswith test OK')


a = 'a%sb%sc'
b = 'foo-bar'

print(a * 5)
print( a %("FOO", "BAR") )

## in regular python the following would fail, but in tpython it is allowed ##
print( a % b )
print( a %([1,2], {'mykey':'myvalue'}) )

