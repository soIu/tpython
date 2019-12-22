with javascript:
	myfunc = function (x,y) { return x * y }
	def myfunc2(x,y) ->float:
		return x * y
	var a = 'hello '
	var b = 'web browser'
	window.alert(a+b)


def test():
	print('hi from tpy interpreter')

	javascript("console.log('calling js from tpy')", returns='void')

	x = javascript("1+1", returns='int')
	print(x)

	y = javascript("1.3+1.2", returns='float')
	print(y)

	z = javascript("'string from js'", returns='string')
	print(z)

	for i in range(10):
		w = javascript("1.1 + %s" %i, returns='float')
		print(w)
		w = javascript("myfunc(%s,%s)" %(i+1, i+2), returns='float')
		print(w)
		w = myfunc2(i+50, i+50)
		print(w)

test()


