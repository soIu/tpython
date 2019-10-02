console.log("begin test");

var a = 1;
var b = 2;
var c = 0;
for (var i=0; i < 1000000; i++){
	c += a + b;
}
console.log(c);
console.log("ok");

