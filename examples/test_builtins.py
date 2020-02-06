print('testing assert')
assert True
assert(True)
assert( 1==1 )
assert 4!=3
print('testing number')
a = 1
print( dir(a) )

print('testing list')
b = [a,2]
print(len(b))
print(dir(b))
print('len of b should be 2')
print( len(b) )
assert len(b)==2
assert any(b)
assert any([])==False
assert any([0, False, None])==False

print('testing dict')
d = {100: 'foo', 'bar':200}
print( d.keys() )
print( dir(d) )
assert len(d)==2

print('testing string')
s = 'mystring'
print(s)
print('len of s')
print(len(s))
print('dir of s')
print(dir(s))
assert len(s)==8

print('testing getattr')
func = getattr(s, 'startswith')
print(func)
print('calling func')
print( func('my') )
assert func('my')

print('testing setattr on a class instance')
class MyClass:
	A=1
	B=2
ob = MyClass()
print(dir(ob))
setattr(ob, 'FOO', 'BAR')
print(dir(ob))
print('test ob.FOO')
print(ob.FOO)

print('testing hasattr on a class instance')
if hasattr(ob, "FOO"):
	print('hasattr test1 OK')
else:
	print('hasattr test1 FAILED')

if hasattr(ob, "XXXX"):
	print('hasattr test2 FAILED')
else:
	print('hasattr test2 OK')

## Python raise an error setting any attribute on a dict,
## the same should be true TPython, but currently below will
## not throw any error, and instead setattr will set an item in the dict,
## d.update = 'XXX' also sets an item in the dict.
print('testing setattr on a dict')
setattr(d, 'FOO', 'BAR')
print(dir(d))
##print('test d.FOO')
##print(d.FOO)  ## this is not allowed
print('d["FOO"]')
print(d['FOO'])

print('d.update')
print(d.update)
print('d.update="XXX"')
d.update = 'XXX'
print('d.update')
print(d.update)
d['update'] = 'XXX'
print(d.update)
print(d['update'])
print(d)

print('testing sizeof')
print( 'sizeof number:',sizeof(1) )
print( 'sizeof string:',sizeof("a") )
print( 'sizeof string:',sizeof("foo") )
print( 'sizeof object:',sizeof(ob) )
print( 'sizeof list:',sizeof(b) )
print( 'sizeof dict:',sizeof(d) )
print( 'sizeof function:', sizeof(func) )

print('testing divmod')
x,y = divmod( 120, 40 )
print(x)
print(y)
assert x == 3
assert y == 0

gv3 = vec3(4,5,6)
gv3.x = 44  ## this fails TODO fixme

def test_vecs():
	print('testing vector types')

	v2 = vec2(1, 2)
	print(v2)
	assert v2.x == 1
	assert v2.y == 2

	v3 = vec3(1, 2, 3)
	print(v3)
	assert v3.x == 1
	assert v3.y == 2
	assert v3.z == 3

	v4 = vec4(1, 2, 3, 4)
	print(v4)

	assert v4.x == 1
	assert v4.y == 2
	assert v4.z == 3
	assert v4.w == 4

	print('testing set x,y,z of vector')
	## note: setting v3.x only works inside a function, not at the global level
	v3.x = 99
	print(v3)
	assert v3.x == 99
	## BUG: setting x on a global should be ok from inside a function, just not at the global level
	assert gv3.x == 4
	gv3.x = 100
	print(gv3)
	#TODO fixme#assert gv3.x == 100

	#note: vec4 only can hold 16bit floats
	for i in range(16384):
		v4.x = i
		if v4.x != i:
			print('hit max size of vector4: ', i-1)
			print(v4)
			break
	assert v4.x == 2048

test_vecs()

print("OK")


