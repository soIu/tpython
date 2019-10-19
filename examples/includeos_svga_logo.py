## compile with: `./rebuild.py --includeos --svga includeos_svga_logo.py`
## note: this requires qemu with qxl enabled, from your qemu source folder run: ./configure --enable-spice
## for help installing qxl spice see: https://chrisrjones.com/articles/build-qemu-with-spice-video-support-for-an-os-x-vm

Logo = '''X22Xmmmmmmmmmmmmmmmmmmm#######ZZUZZZZZZZZZZZZZZZZZZZZ######mmmmmBmWmWmWmWmWmWmWmWmWmXX1||||||vZXXZX#mBmmBmmmBmmBmmBmmBmBmBmBmZZXXS1ivvii|iII1SYXWmWWBWWBWBWmWBWm
ZSXX#####mmmmmmmmmmmmm###Z#ZZZZZZXXZXZXZXZXZXZXZXZZZZZZ#Z##mmmmmmmmmmBmmmBmBmBmmmmm#Xe|+||+|+IliIZX#mmmmmmmBmmmmmmmmmmmmmmmm#221Il|%*||||i||||||lS#mmWmBmmmWmmmW
#XSXU###m###m###m###m###Z#XXZZZZZZZZZZZZZXZZZZZZZZXZZ##Z####m#mmmmmBmBBBWmBBmBBm##XS*|||+|||||+||XZZ##mmmmmmmmmm#XAX#X#XUXS1Ii|||||||||+|i|viivvi|I3$mWmWmBmmWmm
#XSX######mm#mmm#mmm###Z#ZZZZZZZZXZZXZXXZXZZZZZZZZ#U##U###mm#mmmmmmmmmmmmmWmBm#ZY|||||+|||||+|sz|dX1nUXXYYYSXZY*ilvo2ooIl||i|||+|+|+|+|||innnnvlvvii3#mWmmmmW#mW
#XXX####m##m###m#m####UUU#ZZZZZZZZZZZZZZZXZZZUZUZ#Z#Z#Z#U###m#m#m#mmmmmmBmm##SXe|sa>|+|s%||+<u2(|1liiY*i++||li||||lIll||i%|||+||||||||||vI1i|iilIvvivXZW######mm
ZS2S#####mm#########XZZ#ZZ#XZZZZZZZ#Z#ZZ#ZZZZZZ#Z#Z#####U##m#m#m#m#m#mmmmmm#mo2vv2i||<Il||||li||||ivsivivssvasss%vuquaawXi||+|iiil||||||||+|v|iillviIoSSZ#####mB
X2ooX##m#m##m###Z#XXXZZUU#ZZZZZZZZZZZXnn3XnnnnnSXZ#ZZZ#Z######m#m#m#m##mmmmm##Xoo||+||||+|iivi%i|omXZ#Z#U#####mmmBmmm###e+ivvvIl|||++++|||||||iiilIlln2SZ####mmW
Xoo2X#####m####Z#ZZXZXZZXZXZZZXXXXXnnnvnvvnnvnvvnXXZ#Z#U##Z#######m#m#m###m#m##UXoa%issvauwqmmmqm###mmmmmmmmmWmWBWmm#m#X||Ili|||||>+||ii||+|+|iiiivIiIoSZ#####mm
Z2o2S###m#####Z#Z##XXZZZZZZZZXnnvvvnvnvnvnnvnvnnvvvSSXXZ####Z########m##m#m#mmm##ZXXqqmZ#m########mBBBBBBmBmW#mBmBmmm#Zns||||i||vv%|lii|ii||uavi|iivviInZ####mmW
ZXoSSZ####UZZ#Z#UUZZXZZZZZZZX1Ivvnnvnvnnvnvnvnvnlnvi|ivX##U#########m###m#m#mmmmm#######mmm#m##mmmmmBmWmBBBBmBWmWmmm#X1nvlivv|ivvvlii||i|||i11l|||iIvvivX###mmWm
ZZXSX##Z#ZXZXZ#Z#ZZZZZZZZZZZ2llvnvnvnnvnvnvvvlIiiiviiilnU#UUZ#Z#######mm###mmmmmmm#mmmm#mm#mmmmmmBmWmBmmWmBBBBmBmmm#2nnl|vnlivvnnliii||||+++||+|+|iIvvvvZ###mBmm
ZZZZ#Z##ZZZXZZXZZUZZUZZZZZZXlilvnvnvnvnvvliiiiiiiili|i|IX#Z####UZ#######mmm###mmmmm#m##m##mmmmmmmmmmmmBBmBBBBBBBWm#Xnvvivvivvvvvl|+||+|+|||||||ssivnvnodZ#U#mmBB
#ZU#Z##ZZZZXZXZZZXZZZZXXZZZ1llivvvvvIlliiiiiii|iiiii|||lXXZ###U###U########m#m#m#m#m##########mmmmBmmBmmBmWmBBBBmBZIvnvvvvvvvvnv||||+|||ioXXXonvvnoXXSXZ##Z#mmBm
#ZZZ##Z#ZZZXZZZXZZZZXZZZZU2Iiiiiillilvviiii|i|i|iii|i|iinoXSX##Z#Z#Z#########m#############m#mmmmmmmBmmBmBmWmWmWmmeInvnnvvIvnnvli|+||||iomSnnnnnnnXXXXZ##Z###mmB
#XZZUZ#XZZZZZXZZZZZZZZ#ZZZ1iliiiivnoqXXoouvviiiii|ii|i|vnnvnnX#####U#############m##########m#mmmmBmmBmBmWmBmBmBm#cIIIIIlivnvvvi|||||iumXnvnnnvnv1XXXZZ#U####mmm
#XXXZZZZZZZZXZZZZXZZZZZZZIliiiiilnZ#XXZZ#ZZXqowuwvi|iiilvnnvnnXX#Z#Z################m######m#mmmmmmmBmBmBmBBWmWmm#Uqa|++|vnvnli|||+vvd#Svnnnvlvvi<oXZZ#########m
USn2X#ZZZZZZZZZXZZXZZ#ZXlliiiiilvXXXXXXXX########h%liiivnvnvnvnXXX##Z########m####m###m#m#######mmmmmmmBmBmmmBmBm###Up+innvnli||||vvnnvvnnnvivvsivXZ###########m
UoooXZ##ZZZZZZZZXXZZZX2llililiivXXXSSXXXXSSX######eiiiivnvnvnnnXoXXZ########m#####m##m###########mmmmmmmmmBBBWmBmm####|vnnvli|||ivvnvvnnnvnovnvIoXZ#Z#########m#
Zoooo#UUZZZZZZZZZZUZXeIlilIviivXZXXXXZZXXSXXXZ###ZXvilivvnnvnvvnS2SZ########mm#####m###############mmmmmmBmmmBmWmWmB#movnvii|+|innnvnnnvInvnvlvoZUU###########m#
#oo2SX#Z#ZZZ#ZZZZZZZ1vilvvvvlvXUUZXXXZXe1X2SXX#Z#evvIvvvnvnvnnnnnSSZ##########mm####m##m#########mmmmmmmBmmBBBmBmBBW#XSvvii|||vvnnnnnvl|{nnvIndX#############m#m
#Xo2XZ###ZZZZZZX#ZZeIlvvvvvnvoXZZ#ZUZZX=ii|iISXZevvvvvvIvnvnnvvnnXoZ####U#####m####m############mmmmmmmBmmBmmWmWmWmmkvvvii|||ivnnvnvvi||vnouoZX######m#######m#m
ZXXmXZ#ZZZZZZZZZXZeIlvvvvvnnnnXZ#Z#ZZZ1i    +|vnvvvvvvvivvnnvnnvnnXX############m##############mmmmmBmmmmBmBBmWmWmm#1vnii|||ivnnvnnnlsuXXZZ########mm###mmmmmmmm
ZXZXXZZZZZZZZZ#XZ2vIvnvlvnnnnnnX#ZZ#Z#si    +ivvvIvvvvviiIvvnvnvnnXoX####Z####################mmmBmBmmBmBmmBBWmB#ASnvniii|||vnvnnnvnXmZ####m#m#mmmmm##mmmmm#mmmm
#ZXZZZZZZZZZZXZZX1IvnllnnnnnvnnXZ#Z#ZZ##i   |ioXXvvvvvnv|i|vvnnvnvnSoZ########################mmBmmmmmmmmmBBBmBmSvvvvii||||vnvnnvnnX##mmmmmmmmmmmmmmmmmmmmmmmmmm
#ZXXZZZZZZZZZZZ#2vvnIlnnnnnnnnnXZ#ZZ#Z#####ZwqZZXvvvvI2ov|||vnvnnvnnXX########################mmWmBBmBmWmmWmWmmXvvvnii|i||invnnnnnnm#mmmmmmmmmBmmmmmmmmBmmm#mmmm
#ZXXZZZZZZZZZZZX1vnvIvnnnvnnnnn3ZUZ#Z####mmmmm#Zovvvvv22o||||vnvnvnnXnXm#######################mmmmmBmBmmmBmm#Svvnvli|i||ivnnnvnvnX##mmmmmmmBmmmmBmBmBmmmmmmmmmm
#ZXZZZZZZZZZ#ZZXnvnvvnnnnnnnnnv3X#ZUZ###mmmmmm#ennnvvv2S2li|||vnvnnvnSX#####U#################mmBmBmmmBmmBBmXvvvnvviii|||vnnvnnnnnm#mmmmmBmBmmmBmmmmmmmBmBmmmmmm
#ZXXUZZZZZZZZZ#XvvnvvnnnnnnnnnnvXZUZ###mmmmmm#2vvniiIn22Sv|i|||vnvnvnnSXmm############U#U#Z###mmmBmBBmBmBm#Svvnnnvii|i||vvnvnnvnvd##mmmBmmmmmmBmmmBmBmBmmmmBmmBm
#XXXZZZZZZ#ZZ#XXvnvnnnnnnnnnnnnvXX#Z##mmmmBm#Zvvnvi ivS2Soi|i|||vvnnvnXX####U#########U#U#####mmBmBmmBmmm#Svvnnvviiii||<vnnnnvnnnm#mmmBmmmBmBmmmmBmmmmmmmBmmmmmm
#ZXXXZZZUZZZUZZXnvnvnnnnnnnnnnnnnXZ#Z#m#mmmZXnvvnv   inS22l|i||||vnvnvnXZ####U###############mmmBmmBmmBmmSvvnnvnlii|i||vnnvnvnnnnm#mmmmmmBmmmmmBmmmmBmBmBmmmmBmm
#ZSXXZZZZZUZZZZZonnnnnnnnnnnnnvnvXZZ######ZZ1vvnnli  iv2So|||iii|ivnnvnnZ####Z###############mmBmBmBmBmmZvnnvnvlii|i||innnnnnnvndmmmmmBmmmmmBmmmmBmBmmmmmmmBmmmm
#XSSXZZZZ#ZZZUXUXnnvnnnnnnonnnnnnXoZUU###XX1vvnnnnii l22Sni|i|i|ii|IvvInX####################mmmBmBmmmB#nnvnnvniiii|||nnvnvnvnnv3mmmmBmmBmmBmmBmBmmmmmBmBmmmmmmm
ZZXoXZZZZZZZZZZZZXvnnnnnononnnnnXz2XSX###mollvn2onvvnuSSoos|||i|i|||li|vn####U###############mmmBmmBmW#onvnnvns|i|i||innnnnnnvnldBmmBmmmmmBmmmmmmmmBmBmmmmmBmmBm
ZXXSXZZZZZZ#ZZ#XZXonvnnonnnnnnnnmmnooui| i#qvv22nnnn2S2Snnn|i||i||||+|+{vXU##################mmmmBmmmmZvnnnvnnIiii|||vnvnvnvnnvi##mmmmmBmmmmmBmBmBmmmmmmBmmmmmmm
ZXXXXZZXZZZZZUZZZ#XnnnnnnonnnnnX##eX##o|  i#oSo22oonS2S2nnns|||||i||+|+|n3#######mmm#m#######mmmmBmWm#1nnvnvnvli|ii||lnnnnnnvnvi##mBmBmmmBmBmmmmmmmBmBmBmmmmBmmm
ZXXXZZZZZZ#Z#ZZZZZZonnvnononnnnmZ#mv#Uk3pi {XXooo1IS2S22nonn|||i||||+|+|{v#Z####mmm#m#m#####mmmmmmmm#Svnnvnnvnii|||+||vnvnvnnnv|XmmmmmmBmmmmmBmBmBmmmmmmmmBmmmmB
ZXZXZZZZZZZZZZZ#Z#Z#XvnnnnnnnnXZX##o#UZ>SXa+Inno2vlvvIoonnnn%i||||||+|++<vX##mmmmmmmmm#m###mmmmmmm##Cvnvnnvnvl||||+|||i|vnnnvni|dmmmBmmmmBmBmmmmmmmmBmmmBmmmmmmm
ZXXXXZZZZZZZZ#ZZZZ#ZZoonnnnnnq#XZ###3##z+3Xiinoo2oIllvnononon|||||+||++||v3##mmmmmmmmmmm#mmmmmmmm##Zvnvnnvnvvi||+|||+|||inSvnniv#mBmmmBmBmmmmBmBmmmmmmmBmmmmmBmm
ZXXoXZZZZZZ#ZZZZ#ZZ#U#ZoonnnX#ZZZXm#n#Zei||<oS221livnnooooonn%||||+|+|+++|I###mmmmmmmmmm#mmmmmmmmm#1nvnnvnvnl|||||+||+|+|vnnnvvnmmmmBmmmmmBmBmmmmBmmmmmmmmmmmmmm
ZXXSXZZZZZZZZZ#ZZ#Z#ZZ#Zmmm##ZZZZ##mh32lii||IlIiivvn1iInonon1s||||+|++|+|+iX##mmmmBmmmmmmmmmmmmBmB#onnnvnnvl||||+||+|||+|vnvnvvdmBmBmmBmBmmmmmmBmmmmmmmmmmmmmmmm
ZXZXZZZZZUZ#ZUZZ#ZUZ#ZZmmm###ZZZXXmm#mouuoooviiivnnnl|lnnnv1iv||||+|+|++|+|3##mmBmmmBmmmmmmmmBmBmm#Xnvnnvnvi|||||+||+|||<vIIIil3#mmmmBmmmmBmmBmmmBmmBmmmmmmmmmmm
ZXXZZZZZZZZZZZUZZZUZ#ZmmmmXZZZZZmm#mmmmXXXZonv||innnl|innvIs|vi||||+|+|++|+{ZmmmBmBmmBmBmBmBmmBmBm#1nnvnvnv||i||+||+||+i%i||||||3X##mmmmBmmmBmmBmmmBmmmmmmmmmmmm
XoSXXZZZZUZ#ZUZZ#ZZ#Z##mmmZZ#Z#m###mmm#ZSSSSov||vnnnsvvnnviviii|||+|+|=|++|<XmmWmmBmWmmmBmmmBmWmm#1nvnnvnni|i||+||+||iil|i|||||||I***U#mm####mmmmBmmmmmmmmmmmmmm
o2ooZZZZZZZZZUZZZZX####mmm###mmmmmmm#XX2SoS2Xni|vnvnnnnnnvivsis||||+|++++|+|XmmmmBmmmmBmBmBmBmmmBhInnvnnvni||||||+|vvvillii|||||vo%||il?Y1lIXmmBmmmmBmmmmmmm#m#m
2o22ZZZZ#ZZ#ZUZUZX2Z##mmB#ZZmmBmmmB#XZZXXSS2Sn%|innnnvnnnn%Ivili||||++|+|++|3UmBBmBBmBmBmBmBmBBmBevvnnvnvv|||||+||vvnvvlii|||||v21vvvi||iillIY#mmBmBmmmmmmm#m#m#
XooXXZZZZZUZZ#ZZXXXmmmmmm##Z#mmBmBmZZ#ZXSS2S2ovi|nnnnnnnnnv|viii|||+|+++++|+)ZmBmmBmBmBmBmmBmBmB#1nnvnvnvn||||+||vvvvnvv%|iv|vvIsvoXXSn%|||lii3#mmmmmmBmmmmm#m#m
XXXXZZZUZZZUZZUZZX#mmmBm#XXZmmBmmm#ZZZXXS2X2SSvlnnnnnnnnnnv%i%is|i||+|+|+++|iXmBmBmBmWmBmBBmBmBm#vnvnnvvnvi||+||vvnvvnlvI|lvoXvvvXXXY*lIsi||iiiIXX#mmBmmmmmmmm#m
ZXXXZZZZZ#ZZ#Z#ZXX#mmBmmZZZ#mmmB##ZZZXSS2SSS2Snvnnnnnnnvnnnvii|v|||||++++|++|d#mmBmBmmmBmBmBBmWm#vnnvvinvlii+|||vvnvvv|vsivl1vnlonnl|||+Inv|||iiiii1Y#mmBmmmmmmm
Z22ZZZZUZZUZUZ#ZZo#mmm#ZZZZ##mmm#ZZZX2Xon22XS2onnnnnnnnnnvnni||i%i|||+|+|=+||vXmWmmBmWmBBmBmmBmm#nvnvi{nvvv|||iivnvvvvivviv|vnvinnv||v%||||||ivnv%||ilXmmmBmmmmm
ZX2XZZZZZ#ZZ#Z#ZZXnZXZZZXnX##mmm#ZZ#oonvvvX2S2oonnnnnnvnnnnvs|i|n|||||++++|++|I#mmBmBmmBmBmBmmBm#nvvl|vvlvvv|nnvnvnnivvnlIsvnvlvnv||n1||+|+|||vvnnnvi|iXmmmmBmBm
ZXXZZZZZZZUZZ#Z#ZXo22XSSnv3UUZ2XUXZooovliIvnSSXnnnnnnnnnvnvnnii|vii|||+|+|=+|+|3mBmWmmBmmBmBmWmmBovllvvvvvnlinvnnnvvvnvvlvvvnvvnvv|||||+||||||lvnvnooov|3mmBmmmm
ZXZZZZZ#Z#ZU#Z#Z#ZXovvvvvvvXZXnZXSoooIi||ilvvS2nnnnnnnnnvnvvns||vv|||||++++|+|+)BmBmmBmBmBmBmmmBmmpivvvvvvvivvnvvliiIvlIivnnvnvnnv|+||||vs|+|+ivvnnnnnnv|I##mmBm
ZXZXZZZZZZZUZUZ#ZZZX2nnnnvvi1Soooooe1i||i||IvvSonnnnnvnnvvnvnniiini||||++|+++i||XmBmBmBmBmBmBmBmBm2llivvvviinvvI||||ini|invnnvnnv||||||+Il||+||ivvnnnnnnsii1#mmm
XZXZZZZZZUZUZ#Z#Z#ZXo2Snonv|iI22oolii|i|v||lIvnonnnnnnvnvvnvvnsi|vn||||+|=+|+|s+)#BBmWmmBBmBmBmBm#iii|invv|vnv|||+||ivvlvnnvnnnvl|+|%||||||+|||||iivnvnnnv|iIXmm
ZXXXZXZZZZ#ZUZ#Z#ZZoXXXXoonv||i1Ii|lIliuXc|ivIvXnnvnnnvnnInvinn%ivni||||=+|=++Ic|3mmBmmBmBBmBmB#Y||+||||nvvnv|||+||||vvvnnvnvnvn>|||i|i|||I|||||{s|iInnvnooinn##
XXZZXZZZUZZUZ#Z#ZZZoXXZZXnnnl|i|||IvvoqXZoi|vIv2nnnnnnvnnvvn%vnviinv|||+|+++|+|n>|XmBmBmWmmBm#U(|=+|+|+|ivIIi|||||||||Innvnvnnvns||+i|+|||||+|||<ns+|vnnnnnnnv3#
ZXXXZXZZZZ#Z#Z#Z#ZZoSZZXXonnvs|||ivvdXZZZZ||IvInvnvnnnvvnvInsinnvinni|||+|+++|+{n=I#BmBmmmBm#e|+||iiiiiii||+|||iiiii|ivnvnvnnvnvv+|||+||||+|||+||oos||nnnvnnvvv#
ZXZXZZZZZ#ZZ#Z#Z#ZZnX#XXXXXnvvi|illvZZZZZZ%|IIvIvnnvnnnInvlnvivvnivns|i||++|++++Is|3#BmBBmBmmp=|||ii|i|||||ii||||i||ivvnvnnnvnnvv>||+||||||+|+||iXXo%|Ivnnnnnvvm
ZZXZZXZZZZUZ#Z#ZZ#1nXXXXX#Xnnvvi|llvZZZZZ#c|lvIIvvnnvnn%v1iIniinnvlnn||||++++|+|+I>|XBmBmBmBmma+||||i|iiiiiiiiis%ilivvvnnvnvnnvnns||||+||||||||+vlnos||nnvnvnlnm
ZXZZZZZ#Z#ZZUZ#Z#XnnoZXXUXXoovni|lInZZXZZZz|lvIIvvnnvnnlii|lvs|vnnvvn%||||+|=|+++|v>I#mBmBmBmBmo>+|iiiii|i|ii||{*SSsvvnvnnvnnvnvvns|+|||+||||+||ilvX>||InnnnvidW
ZZZZZZUZZZ#ZUZ#ZZXvnnXXXX2SonnviillvZZXZZ#o|lIIvInvnvvvvlvviIviinvvvnv||||++|||||+|1|3mmBmBmWmmmma||||iiii|||||<as|{nvnnvvnnvnvnnv||||+||+|||||||||||<iinnvnlnmm
ZZZZZZZ#Z#ZZUZZ#UnnnXXXXS2XXnnvvIlIIXZXZXZXiiIvlvvvnvnvnnvvvlIs|vnnvvvi|||||||||<|+|i|XBmBmBmmBmm#o|||i||||iauommmzivnnvvvnvnnnvv||+|+||+||+|+|vaiauvvnvnvnvvmmm
ZZZZZ#ZZUZZ#ZZ#ZZnvnXSXS2SSXonnvvIlIvXZZZZ#c|IIvlvvnvvnvnvvvvvli|ivnvvi||||+||||is+|+|)$mBmBmBmBmBmwa||+|<um##mmmBZinvnnnnvnnvnvi||||||+||+||||nonXXvnnnnnnvm#mB
ZZZZZZUZUZ#ZZZZ#ZvnoXSXSSSSXoooonvIIvvZXXZZz|lvlIvnvnvvvvnvvsilv||innIvii|||+||||I>|=||3#mBmWmmBBmBmmouuwdmmmmBBBmCnvnvnvvnvnvvi||+%|||||+||+|vnonlvvnnvnvndmmmm
ZZZZ#ZZZUZZZZZZZnvoXS2XS2SSSXXSooonlvvnZZZZXiivIIvvnvvnvnnnvviilsi|Iovvvv||||+||||l=|++=3mmBmmBmBmBmmBBmmBBBmBmmm#nvinnvnvnvvvi||+vi|+|+|||+<vnnInvvlnvnnnm#mmmB
ZZZZZZZ#ZZ#ZZZ#XnndX2SXSS2SXmSoS2ovvoonXXZZZilIlIInvvnvvvvnvvv|lis||nnvvov|||||||||i++||i3#mmBmBmBmWmBmWmmmBmmBBmkvivvnvnvnvvv>||ve|+||||+||vnvvvvvvlnnnnd##mmBm
ZZUZZZZZZZZZZ#ZnvdoS2nXSoS2m#mXoSnvvo2oXXZZZovIIvlnnnvvvnvvnnvi|lls|iInInoii||||||||||++|||YS#mBmBmmmmBmmBBmBBmm#lvlvnvnvnvlIl||ve=||i||+||<nlvvvvlivvnvX#mmmBmm
ZZZZZZZZZ#ZZ#X2nno22Svn1v1d####moSvvnoXXXZZZXovlIInZXovnvvnvnvii|lI%||vvvnvvs||||||||||++|i++*YU##mBmWmmBmmmm#Y1linnnvnvnviiv||v1|||ii|+|||vvivvvvi|vnnommmmmmmm
ZZZXZZZZZZZ#ZXvooo222oliIIl3#m##Z2vvvnXSZZZXZXvIvlvZUXovvvnvvnvi||lI%|ivvnn#m%||||||i||||||iiiii||*YXSVVVVS*1illvnnvvnvnIlvv||il|||ii|+||+ivlinnnvvvnnommmmmBmBm
ZZZZZXZZ#Z#ZXvd#o22S2Xii||i3#mmm&ovvvvSSZZZZUXovlIIXZ#onvnvvnvnli|iili|ivvv3#p>||||i|||||||iii|ilIsi||||iiivllvvvnvnnvnlvo1||||||+|i|+||||vvvvnnvoSvnndmmmBmmmmm
ZZXZXZZZZZZZSnmXo2222Zci||inmmmmZovvvvSSXZZUZXXlIvlXZZZovvvnvvvnli||lIiiiIvvX#z||||||||||||||||||||ivvvnvvnvnvvnvnvnvvvl1i|||+|+|||+|||+|vnnnnnvnnvnnv#mmmmmBmBm
ZZXZZZZUZ#ZZvd#oo2So2X1i||ldmmmmX1vvvvXXXXZXZXSvIIlnZ#ZXnnvvvnvnvIi|iilliii|I3#%||||||||i|||||||||||IvnIIIvnvnnvnvnvvvi||||+|||||+||+|+|vvlivnvnvnvnvn##mBmmmmmm
ZXZZZZZZZZZonm#ooSonnvvs|inmmmm#SvvvvoXXXXXXXXXzvIInZXZXXvvnvvvnvnvliiilIvs|||*1||||i||i|||i||||||||iii||ivvnvvnlIIilvi||||||+|+|||+|||iviivvnnvIliilnXmmmmBmBmB
ZZZZZZZZZZXvdmZoo2vvvvviilm#mmmX2vvvnSXXXXXXXZXovIInXXXXXonvvnvnvvvIliiiilInv|i|is|i||i||||||||i||i|||||||iiIvvl||||||||||+|+||%||+||||vnovnnvviiiii|iIX#mmmmmmm
ZZXZZZZXXZnnmmXoonvvvvliin##mm#XovvvnXSXXXXXXXXXvIIvXZXXXXonvvvnnInvlIlliiil1vi|iIXXa||ii|||||i|||||||||||||ii|||i|||||+|+||<uvl||||+|vvnnnnvliii|i|ii|i3XmmBmmB
ZZZZZX2XZ2nmmmXonvvvvlIiidmmmmXXnvvvX2XXXXXXXXXXzvIvXXXXXXZonvnvnvvvvllIiiiillIv|||1Xz||+||||||||||||||i|||||||iiuSS||||||||nvl||+|+|vvnXnvvli|i|i|i|iiiivXU#mmm
ZZZZZ2oXXvX###onvvvIlII|vmmmmmZSvvIv2XXZXXXXXZXXovlIn#XXXXXXonvvvnnvvvllvIviv%ilIv|iiIi|||+||+||+||||||i1i||||i|||||||i|||||vi|||+||innnnnniiiiiIvliiiiiiIvv#mBm
ZZXZXnXXnn#mm#nnvvvlIIlidmmmmmZ2vvInXXXZXZXXZZZXXvIvnXXXXXXXZonvnvnvvnvvlIlIlIvilili|||||+||+||+|||+||||||||||+||ii||||||ivIi||i|||vvnivnvl|iivvnvnvnliivvooW#mm
ZZZXoXX2vd###XnvvvIIIIiiXmmmmmXovvloXXZXZXZXXXZXX1vlvvXXXXXXXXonvvvnnvvnnvvIIvIIliillii||||+||+||+|||+|+|+|+|+||+||+|+|+|vl||+vi|=vvnIvnvliiivvnnnnvvliIvnoX##mm
ZZXSoXX1nm###XvvvvvlIl|v#mmmm#XnvIvXSXZZXZXXZZXXSovIIII1XXXXXXZovnvvvnvvnvnvvvlIIlliilli||||||||||+|+|||+||||||+||+|||+|vl|||v1||vnnvvnvlivvvvnnvnvnvilvvonXZm##
ZXXnXXXvdm##ZXvvvvlIIiin##mmm#SvvlnXXXZZXXXXXXXXXSoIvlIIv1ZXXXXZonvvnvvvvnvvvnvvvvIlliiilii||||l|||||+|+||+||+|||i|||||%i|vovi||vnnnnnvlivvvvnvnnnvviiIvnnnZ#mm#
X2XZ#X2nm##ZZXIvvvIIl|l3##mmmZ2vvIXSXXXXXXZXZZXXX2XvlIliiiI12SXZZonvnvnvnvnoXXoIvnvvvllilllli|||||||+||||+||+||||||ivIl|<uel|||ivnnnvnvivvnnnnnnvvviiIvnoom#mmm#
om#ZZXnd##UZZovvvvlIliIdU#mm#XSvIvXSXXXXZXXXXXZXSoSnvvli||i|||lIX#XXoXovvvnvvnX|ivIIvnvvvllllili|iis|||+||||||isvvvvvi||Ii||v>ivnonvvnlvvnnvnvnvvvillvvnXXmmmmm#
##XXZXnm##ZZZovvvvlvlIId##mm#X2vIoXXXXXZXXXXZZXXX1vS2nvviv%|||||I#XZoXSovnvvvnvs|i|ii|IIvnvvvvvivvivnviIlIlIvvvvvvnvi|||+iinvvnnnnIvoonvnnvnnnnvliilvvn2m#mmmmmm
ZXXZXXn##ZZZZnvvvIIIlIv#Zmm##XnvvXXXXXXXXZZZZZZZSlvvnonnvilviiiIlXXXXXo3ovvnvvvvvvsi||i|ilIInnnvvvvnvnvvvnvvnvnnnnns|||ivvnvnnv1llvoonvnnIvvvvliillvnnom##mmBmmm
XXXXZ23###ZZXvvvvlIIIIn###mmZXnvvSXZXXXZZZZZZXX1vIvIvn2nviiiIvlIlIXXSSXXnnnvvnvnvvvvvv|iil|iIIIvllvvnnnnnnnnnnnnvvIi|lvvvnvnvvvIivonnvnnvlvnnvillvvnnoX##mmmBmBm
UZZZZndm#ZZZXvvvvIvIIIdZ##mmXSnvvXXXXXS11nSY1vvvvIvvnvn2nvillilIlvInS22SXoovnvvvvvvvvviivvvIIvilvllvvvvvvvIvIvvvvli|vvvvnvvlvvvilnvvvnvviIvnXovvvnnnoXmBmmmBmmmm
ZZUZXnm#ZZZXevvvvonlIId####mXSIInoon1vIvvvlIvvvvlIIIvlvvSnvlIlllIIvoSSS2SSXoovvnvnvnvvviiivvvvvvvvvvvvvvvvvvvv1li|ivvvnvvvIvlliivnvvnnvvivdXXnnnnnn2XmWmmmmmmmmm
ZZZZomZ#ZZXXnvvvnonIIv##U###ZSlvvonvvvvIvIvvIvIlIvIIlllIvnnnIllllvnXX22S2SSXXqovvvvvvvvvi|iilvlvvIIlIIvvvvvvIlilivvvvnvvnvvnvvvvnvnnnvliuX2oooonnoXm#mmmmmBmBmBm
ZXXSnX##ZXZXvvvv22nvln##Z###Z2lvv2vvIvIvIvIvvIIvIlIllIIlII2oIvooXoXSSSooS2XXZ##movnvIIvvvIii|lli|i|iii|||iilllvvvvllvvnvvvvnvvIvvvvlliin2ooS2SooSXmU#mmmmBmmmmmm
ZZZXo3###ZZXvvvo22nvld#Z####ZoIvnovvvvIvIvvllIIIIIIIlIoonnn2XXSSSSS2nnnXXSXXn####XovvvviIvvvviilli||i|||iiivvvIiilvvnvllvvnvvviilililvoXnSSSXXSXX###mmBmBmmmmBmm
ZXXZ2nX#Z#ZXnvo22SovvXZ#####melInnvvvvIvvIlIvIIvllIooUXXXXSS2SSS22onoSSXXXXomU#####qoovvvilIvviiiliiilvvvvIliiliiivnllvvvvvviiinvvnouXnn2S2XZZ##mmmmmmmmmmmBmmm#
ZZZXSnX#Z#XXovS222nv2o##Z####1ilvvvvvIvvlIIIIIvvnowZXXXXX2SSXSS2SooS2Soo2Xm#####mmmmmmmwuvvvilll||iIvlivllvivvviiivvnvvvlliiiu2So2XnXvoXSXZmmmm#mmmmmBmBmBmmmmm#
XZZZXonX#ZZXXn2SS2noX2X####m#viIIvvvvIIlIvlvvnoXZZXXXXSSXXX2S2XS2oS2S2o2omZ###mmmmmmmmm#mqwowouuaasiillIvnvnvnvvnvnnvnvvllvvnnnoo2o2oqmqm#mmmmmmmBmBmmBmmmmmmm##
ZXXXZXnXZZZXXSSSoonXX2XZ####hlillIlllvlvlIvndZZXXZXX2SSS2SSXSSSooSSSSo2Xm####mmmmmmmmmmm#m#mmmmmmmmmmwavillIIvvIIIllvvvnnoooowmqmmm#mmm##mmmmBmmBmmmmmmmBmmmmm##
#ZZZZZooXnoXX2nnnvn2Som####Z1llllllIllIlvvdXXXZXXSXXXX2SSS2SSSooSXXSooX####mmmmmmmmmmmmmmmmmmmmmmmmm####moa|iiiiivawwmm#mmmBBm#####mmBmmmmmmBmmmmmmmBmBmmmmmm###
ZZ#ZZXZX2oooonnvvno2ooX####elilllllllIIooZXXSSXXXX2SSSXS2SSS2ooXS2S2oX####mmmmmmmmmmmmmmmmmmmmmmmmBmmmmmm##mwwwmm#m#####mmBmmmmmmmmmmmmBmBmBmmmBmmBmmmmmmmmmm###
ZZXZZ#XXX2ooonnnno22SSX###ZvlllillllIndXUZZZXXS2XXXXSSXXSS22ooXSXX2oX#####mmmmmmmmmmmmmmmm#mmmmmBmmmBmmBmmmm##m##mmmmmmmmBmmmBmBmBmmBmmmmmmmmmmmmmmmmmBmmmmm####
ZZZZZZZZZXXX2Sono22222oX#Zn2nvlilllvoZXZZZZZXXXXSSSSSSSSXX2noXS2SoSXmZ###mmmmmmmmmmmm#m#mmmmmmmmmBmBmmBmmmmmmmmmmmBmBmBmBmmmBmmmmmmBmmBmBmmBmmBmmmmmmmmmmm#m####
ZZZZZZZZZZZXZXXS222S2S22XooonlllIvuXXXZXXXXXXXXSSS2SSSSSS1oXZXS2XXmZ###mmmmmmmmmmmmm#mmmmmmmmmmmBmmmmmmmmBmmBmBmBmmmmmmmmmmmmmmmBmmmmmmmmmmmmmmmmmmmmmmmm#######'''

with c++:
	import <timers>
	import <x86intrin.h>
	static char backbuffer[320*200] __attribute__((aligned(16)))
	def set_pixel(int x, int y, char cl):
		if x >= 0 && x < 320 && y >= 0 && y < 200:
			backbuffer[y * 320 + x] = cl
	@module( mymodule )
	def redraw( logo, shift ):
		int y = 0
		while y < len(logo):
			tp_obj line = logo[y]
			int x = 0
			while x < len(line):
				char color = line[x]
				set_pixel(x,y, color+shift.number.val)
				x += 1
			y += 1
		VGA_gfx::blit_from(backbuffer)
		return None
	@module( mymodule )
	def reset():
		VGA_gfx::set_mode(VGA_gfx::MODE_320_200_256)
		VGA_gfx::clear()
		VGA_gfx::apply_default_palette()
		return None


import mymodule

lines = Logo.splitlines()

def test():
	s = -128
	for i in range(100000):
		mymodule.reset()
		mymodule.redraw( lines, s )
		s += 1
		if s >= 32:
			s = -128

test()
