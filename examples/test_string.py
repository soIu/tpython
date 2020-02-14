print('testing a short string `hi`...')
print('hi')

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

abc = ','.join(['A', 'B', 'C'])
print( abc )
print( abc.replace(',', '_') )
cba = abc.reverse()
print(cba)

ln = '                          '
for c in ln:
	if c==' ':
		continue
	else:
		print('long line of spaces failed')
		assert 0

## in regular python the following would fail, but in tpython it is allowed ##
print( a % b )
print( a %([1,2], {'mykey':'myvalue'}) )

## 4bit strings can be up to 24 chars long, and can only contain: `ABCD!$%&*+-=?@_`
print('testing 4bit strings')
e = 'ABCD!$%&*+-=?@____'

print(e)
assert e[0] == 'A'
assert e[1] == 'B'
assert e[2] == 'C'
assert e[3] == 'D'
assert e[4] == '!'
assert e[5] == '$'
assert e[6] == '%'
assert e[7] == '&'
assert e[8] == '*'
assert e[9] == '+'
assert e[10] == '-'
assert e[11] == '='
assert e[12] == '?'
assert e[13] == '@'
assert e[14] == '_'

print("OK")


