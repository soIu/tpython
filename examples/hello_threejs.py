import random

with javascript:
	import THREE
	console.log(THREE)
	Meshes = []
	def setup_threejs():
		width = 640; height = 320
		ren = new THREE.WebGLRenderer( { antialias: true, canvas:document.getElementById('canvas') } )
		ren.setPixelRatio( window.devicePixelRatio )
		ren.setSize( width, height )
		scn = new THREE.Scene()
		cam = new THREE.PerspectiveCamera( 45, width/height, 0.01, 10000)
		cam.position.x = 40
		light = new THREE.PointLight()
		light.position.set( 0, 100, 90 )
		scn.add( light )
	def make_cylinder(x,y,z) ->int:
		radiusTop=0.3; radiusBottom=0.6; height=0.5
		geo = new THREE.CylinderGeometry( radiusTop, radiusBottom, height )
		mat = new THREE.MeshPhongMaterial()
		mesh = new THREE.Mesh( geo, mat )
		mesh.position.set(x,y,z)
		mesh.rotation.set(Math.random(), Math.random(), Math.random())
		scn.add( mesh )
		Meshes.push( mesh )
		return Meshes.length-1
	def make_sphere(x,y,z) ->int:
		radius=0.2; detail=1
		geo = new THREE.IcosahedronGeometry( radius, detail )
		mat = new THREE.MeshPhongMaterial()
		mesh = new THREE.Mesh( geo, mat )
		mesh.position.set(x,y,z)
		scn.add( mesh )
		Meshes.push( mesh )
		return Meshes.length-1
	def animate():
		requestAnimationFrame( animate )
		for (var i=0; i<Meshes.length; i++):
			var m = Meshes[i]
			m.rotation.x = m.rotation.x + 0.01
			m.rotation.y = m.rotation.y + 0.02
			x = m.quaternion.x
			y = m.quaternion.y
			z = m.quaternion.z
			m.material.color.setRGB( x,y,z )
		ren.render( scn, cam )


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

MeshesHiddenInfo = {}

def test():
	print('three.js test')
	setup_threejs()
	y = 0
	for ln in logo:
		x = 0
		for char in ln:
			id = -1
			if char == ' ':
				pass
			elif char == 'Q':
				id = make_cylinder(x, y, -60)
			else:
				id = make_sphere( x, y, -60 )
			if id != -1:
				hidden_data = random.random()
				MeshesHiddenInfo[ id ] = hidden_data
				print(id, ':', hidden_data)
			x += 1
		y -= 1
	animate()

test()


