import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs
from io import StringIO

class SimpleRoute:
    def __init__(self):
        self.routes = {}
    
    def route(self, path, method='GET'):
        def decorator(func):
            key = f"{method} {path}"
            self.routes[key] = func
            return func
        return decorator
    
    def find_route(self, path, method):
        key = f"{method} {path}"
        return self.routes.get(key)

# Tạo instance framework
app = SimpleRoute()

# Định nghĩa các route
@app.route('/hello', 'GET')
def hello(params):
    return json.dumps({'message': 'Hello, World!'})

@app.route('/user', 'GET')
def get_user(params):
    name = params.get('name', ['Guest'])[0]
    return json.dumps({'user': name})

@app.route('/api/data', 'POST')
def post_data(params):
    return json.dumps({'status': 'Data received'})

# RequestHandler cho server
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        handler = app.find_route(path, 'GET')
        
        if handler:
            response = handler(query_params)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        handler = app.find_route(path, 'POST')
        
        if handler:
            response = handler({})
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode())
    
    def log_message(self, format, *args):
        pass  # Tắt log mặc định

# Chạy server
if __name__ == '__main__':
    PORT = 8000
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Server chạy trên http://localhost:{PORT}")
        print("Các route có sẵn:")
        print("  GET /hello")
        print("  GET /user?name=John")
        print("  POST /api/data")
        httpd.serve_forever()