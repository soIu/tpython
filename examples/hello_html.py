with javascript:
	var a = 'hello '
	var b = 'web browser'
	window.alert(a+b)

print('hi from tpy interpreter')

javascript("console.log('calling js from tpy')", returns='void')

x = javascript("1+1", returns='int')
print(x)

y = javascript("1.3+1.2", returns='float')
print(y)

z = javascript("'string from js'", returns='string')
print(z)

