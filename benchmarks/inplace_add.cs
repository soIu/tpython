using System;

class HelloWorld {
	static void Main() {
		Console.WriteLine("begin test");

		var a = 1;
		var b = 2;
		var c = 0;
		for (var i=0; i < 1000000; i++){
			c += a + b;
		}
		Console.WriteLine(c);
		Console.WriteLine("ok");
	}
}
