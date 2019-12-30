
with c++:
	import <memory>
	class Record:
		std::shared_ptr<Record> PtrComp
		int Discr
		int EnumComp
		int IntComp
		const char* StringComp
		def __init__(std::shared_ptr<Record> PtrComp, int Discr, int EnumComp, int IntComp, const char* StringComp):
			this->PtrComp = PtrComp
			this->Discr = Discr
			this->EnumComp = EnumComp
			this->IntComp = IntComp
			this->StringComp = StringComp
		def copy() -> std::shared_ptr<Record>:
			return std::make_shared<Record>(PtrComp, Discr, EnumComp, IntComp, StringComp)
	int TRUE = 1
	int FALSE = 0
	int IntGlob = 0
	int BoolGlob = FALSE
	char Char1Glob = '\0'
	char Char2Glob = '\0'
	std::shared_ptr<Record> PtrGlb
	std::shared_ptr<Record> PtrGlbNext
	int Ident1 = 1
	int Ident2 = 2 
	int Ident3 = 3
	int Ident4 = 4
	int Ident5 = 5
	std::vector<int> Array1Glob
	std::vector<std::vector<int>> Array2Glob
	def Func1(char CharPar1, char CharPar2) ->int:
		char CharLoc1 = CharPar1
		char CharLoc2 = CharLoc1
		if CharLoc2 != CharPar2:
			return Ident1
		else:
			return Ident2
	def Func2(const char* StrParI1, const char* StrParI2) ->int:
		int IntLoc = 1
		char CharLoc = '\0'
		while IntLoc <= 1:
			if Func1(StrParI1[IntLoc], StrParI2[IntLoc+1]) == Ident1:
				CharLoc = 'A'
				IntLoc = IntLoc + 1
		if CharLoc >= 'W' and CharLoc <= 'Z':
			IntLoc = 7
		if CharLoc == 'X':
			return TRUE
		else:
			if StrParI1 > StrParI2:
				IntLoc = IntLoc + 7
				return TRUE
			else:
				return FALSE
	def Func3(int EnumParIn) ->int:
		int EnumLoc = EnumParIn
		if EnumLoc == Ident3:
			return TRUE
		return FALSE
	def Proc2(int IntParIO) ->int:
		int EnumLoc = 0
		int IntLoc = IntParIO + 10
		while true:
			if Char1Glob == 'A':
				IntLoc = IntLoc - 1
				IntParIO = IntLoc - IntGlob
				EnumLoc = Ident1
			if EnumLoc == Ident1:
				break
		return IntParIO
	def Proc7(int IntParI1, int IntParI2) ->int:
		int IntLoc = IntParI1 + 2
		int IntParOut = IntParI2 + IntLoc
		return IntParOut
	def Proc3(std::shared_ptr<Record> PtrParOut) -> std::shared_ptr<Record>:
		if PtrGlb != nullptr:
			PtrParOut = PtrGlb->PtrComp
		else:
			IntGlob = 100
		PtrGlb->IntComp = Proc7(10, IntGlob)
		return PtrParOut
	def Proc4():
		int BoolLoc = Char1Glob == 'A'
		BoolLoc = BoolLoc || BoolGlob
		Char2Glob = 'B'
	def Proc5():
		Char1Glob = 'A'
		BoolGlob = FALSE
	def Proc6(int EnumParIn) ->int:
		int EnumParOut = EnumParIn
		if not Func3(EnumParIn):
			EnumParOut = Ident4
		if EnumParIn == Ident1:
			EnumParOut = Ident1
		elif EnumParIn == Ident2:
			if IntGlob > 100:
				EnumParOut = Ident1
			else:
				EnumParOut = Ident4
		elif EnumParIn == Ident3:
			EnumParOut = Ident2
		elif EnumParIn == Ident4:
			##pass
		elif EnumParIn == Ident5:
			EnumParOut = Ident3
		return EnumParOut
	def Proc8(std::vector<int> Array1Par, std::vector<std::vector<int>> Array2Par, int IntParI1, int IntParI2):
		int IntLoc = IntParI1 + 5
		Array1Par[IntLoc] = IntParI2
		Array1Par[IntLoc+1] = Array1Par[IntLoc]
		Array1Par[IntLoc+30] = IntLoc
		for IntIndex in range(IntLoc, IntLoc+2):
			Array2Par[IntLoc][IntIndex] = IntLoc
		Array2Par[IntLoc][IntLoc-1] = Array2Par[IntLoc][IntLoc-1] + 1
		Array2Par[IntLoc+20][IntLoc] = Array1Par[IntLoc]
		IntGlob = 5
	def Proc1(std::shared_ptr<Record> PtrParIn) -> std::shared_ptr<Record>:
		auto NextRecord = PtrGlb->copy()
		PtrParIn->PtrComp = NextRecord
		PtrParIn->IntComp = 5
		NextRecord->IntComp = PtrParIn->IntComp
		NextRecord->PtrComp = PtrParIn->PtrComp
		NextRecord->PtrComp = Proc3(NextRecord->PtrComp)
		if NextRecord->Discr == Ident1:
			NextRecord->IntComp = 6
			NextRecord->EnumComp = Proc6(PtrParIn->EnumComp)
			NextRecord->PtrComp = PtrGlb->PtrComp
			NextRecord->IntComp = Proc7(NextRecord->IntComp, 10)
		else:
			PtrParIn = NextRecord->copy()
		NextRecord->PtrComp = nullptr
		return PtrParIn
	def Proc0(int loops) ->int:
		PtrGlbNext = std::make_shared<Record>( nullptr, 0, 0, 0, "" )
		PtrGlb = std::make_shared<Record>(PtrGlbNext, Ident1, Ident3, 40, "DHRYSTONE PROGRAM, SOME STRING")
		auto String1Loc = "DHRYSTONE PROGRAM, 1'ST STRING"
		Array2Glob[8][7] = 10
		int ops = 0
		for i in range(loops):
			Proc5()
			Proc4()
			int IntLoc1 = 2
			int IntLoc2 = 3
			int IntLoc3 = 0
			auto String2Loc = "DHRYSTONE PROGRAM, 2'ND STRING"
			int EnumLoc = Ident2
			BoolGlob = ! Func2(String1Loc, String2Loc)
			while IntLoc1 < IntLoc2:
				IntLoc3 = 5 * IntLoc1 - IntLoc2
				IntLoc3 = Proc7(IntLoc1, IntLoc2)
				IntLoc1 = IntLoc1 + 1
				ops += 1
			Proc8(Array1Glob, Array2Glob, IntLoc1, IntLoc3)
			PtrGlb = Proc1(PtrGlb)
			char CharIndex = 'A'
			while CharIndex <= Char2Glob:
				if EnumLoc == Func1(CharIndex, 'C'):
					EnumLoc = Proc6(Ident1)
				CharIndex = chr(ord(CharIndex)+1)
				ops += 1
			IntLoc3 = IntLoc2 * IntLoc1
			IntLoc2 = IntLoc3 / IntLoc1
			IntLoc2 = 7 * (IntLoc3 - IntLoc2) - IntLoc1
			IntLoc1 = Proc2(IntLoc1)
			ops += 1
		return ops
	@module( mymod )
	def pystones(loops):
		print("enter pystones...")
		Array1Glob = std::vector<int>()
		for i in range(51):
			Array1Glob.push_back(0)
		Array2Glob = std::vector<std::vector<int>>()
		for i in range(51):
			Array2Glob.push_back( Array1Glob )
		int ops = Proc0(loops)
		print(ops)
		return None


import mymod

def main():
	print('enter main...')
	##LOOPS = 100000
	LOOPS = 2
	mymod.pystones( LOOPS )
	print(ops)

main()
