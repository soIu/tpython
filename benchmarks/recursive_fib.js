// The Fibonacci Sequence //

function fib(n){
	if (n == 0){
		return 0;
	} else if (n == 1){
		return 1;
	} else {
		return fib(n-1) + fib(n-2);
	}
}

function run_test(){
	var a = fib( 32 );
	console.log(a);
}

function main(){
	console.log('enter main...');
	run_test();
}

main();
