#!/usr/bin/python3
import http.server
import socketserver
import base64, subprocess
from http import HTTPStatus

class Handler(http.server.SimpleHTTPRequestHandler):
	def do_GET(self):
		self.send_response(HTTPStatus.OK)
		self.end_headers()
		#print(self.path)
		if self.path.startswith('/recompile'):
			src = base64.b64decode( self.path[ len('/recompile?') : ] ).decode('utf-8')
			src = src.replace('<br>', '\n').replace('&lt;', '<').replace('&gt;', '>')
			tmpfile = '/tmp/tpy-webserver-user-temp.py'
			open(tmpfile, 'wb').write(src.encode('utf-8'))
			try:
				info = subprocess.check_output(['./rebuild.py', '--ode', '--aot', '--server', '--html', tmpfile])
				info = info.decode('utf-8')
				print(info)
				info = '<a href="/">reload</a><hr/><pre>%s</pre><hr/><a href="/">reload</a>' %info
				self.wfile.write(info.encode('utf-8'))
				#subprocess.check_call(['./rebuild.py', '--ode', '--aot', '--server', '--html', tmpfile])
				#self.wfile.write(b'COMPILE OK')
			except:
				print("COMPILE ERROR")
				self.wfile.write(b'<h1>COMPILE ERROR</h1><a href="/">reload</a>')				
		elif self.path == '/tpython%2B%2B.js' or self.path == '/tpython++.js':
			self.wfile.write( open('./tpython++.js','rb').read() )
		elif self.path == '/tpython%2B%2B.wasm.gz' or self.path == '/tpython++.wasm.gz':
			self.wfile.write( open('./tpython++.wasm.gz','rb').read() )
		elif self.path == '/':
			self.wfile.write( open('./tpython++.html','rb').read() )
		else:
			self.wfile.write(b'Hello world')

httpd = socketserver.TCPServer(('', 8080), Handler)
httpd.serve_forever()

