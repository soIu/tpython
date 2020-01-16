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


