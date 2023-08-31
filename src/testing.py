from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with open(self.path[1:], 'rb') as file:
                content = file.read()
                self.send_response(200)
                # self.send_header('Content-type', 'application/octet-stream')
                # self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                self.wfile.write(content)

            # else:
            #     self.send_response(404)
            #     self.end_headers()
            #     self.wfile.write(b'File not found')

        except Exception as e:
            print(e)
            # self.send_response(500)
            # self.end_headers()
            # self.wfile.write(str(e).encode())

def run_server():
    host = '127.0.0.1'
    port = 8000
    server = HTTPServer((host, port), MyHTTPRequestHandler)
    print(f'Server started on http://{host}:{port}')
    server.serve_forever()

if __name__ == '__main__':
    run_server()
