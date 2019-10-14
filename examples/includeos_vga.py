## this demo is compiled with: `./rebuild.py --includeos --vga includeos_vga.py`
import vga
import random


logo = [
'                                           s/                                   ',
'         ]QQQQQQQQ( QQQQma           _c    df                                   ',
'         "!"?$P!"?` QF"??WL          ]E    df                                   ',
'             df     Q;   ]Q .      . ]E .  df sa.     _ac     . _a,             ',
'             df     Q;   <Q 4L    mf]QQQQf dLmWWQ/   yQQWQ/  ]EjQQQc            ',
'             df     Q;   j@ )Q.  <Q` ]k    dQ.  4h  ]W.  4Q  ]Qf  ]Q            ',
'             df     QwaamQ.  W[  jF  ]E    df   )Q  m[    Q( ]@    Q;           ',
'             df     QP???.   ]m .Q(  ]E    df   =Q  Q(    df ]E    Q;           ',
'             df     Q;       -Q;]@   ]E    df   =Q  Q(    mf ]E    Q(           ',
'             df     Q;        4Lmf   ]E    df   )W  $L   .Q( ]E    Q(           ',
'             df     Q;        )QQ`   ]Qaa, df   =Q  ]Wc _y@  ]E    Q(           ',
'             df     Q;         WF     ?QW[ df   =Q   ?QQQD.  ]E    Q(           ',
'                              .Q(                      --                       ',
'                            ._y@                                                ',
'                            )Q@.                                                ',
]

def draw_random():
	for x in range(320):
		for y in range(240):
			char = random.random()*255
			color = random.random()*128
			#vga.draw('█', 2, x, y)  ## can only be drawn as white
			vga.draw(char, color, x, y)

def draw_logo():
	y = 0
	for ln in logo:
		x = 0
		for char in ln:
			color = random.random()*16
			vga.draw(char, color, x, y)
			x += 1
		y += 1

def main():
	vga.initialize()
	#for i in range(30):
	#	vga.clear()
	#	if random.random() > 0.5:
	#		draw_random()
	#	else:
	#		draw_logo()
	vga.clear()
	draw_logo()

main()
