print( ['X', 'Y', 'Z'] )

s = 'x y z'
print( s.split(' ') )

m = '''line1
line2
line3'''
print( m.splitlines() )

a = 'a%sb%sc'
b = 'foo-bar'

print(a * 5)
print( a %("FOO", "BAR") )

## in regular python the following would fail, but in tpython it is allowed ##
print( a % b )
print( a %([1,2], {'mykey':'myvalue'}) )

