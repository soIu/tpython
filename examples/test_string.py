a = 'a%sb%sc'
b = 'foo-bar'

print(a * 5)
print( a %("FOO", "BAR") )

## in regular python the following would fail, but in tpython it is allowed ##
print( a % b )
print( a %([1,2], {'mykey':'myvalue'}) )

