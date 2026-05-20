import http.server, socketserver, os
PORT = int(os.environ.get('PORT', 8000))
os.chdir('/Users/viveksovani/Desktop/BhagvadgitaMarathi')
handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(('', PORT), handler) as httpd:
    print(f'Serving on port {PORT}')
    httpd.serve_forever()
