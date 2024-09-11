from http.server import BaseHTTPRequestHandler, HTTPServer

# Constants for page URLS
MAIN_PAGE = "static/html/mainpage.html"
LISTINGS_PAGE = "static/html/listings.html"
NOT_FOUND_404_PAGE = "static/html/404.html"

def server(url):
    """
    url is a *PARTIAL* URL. If the browser requests `http://localhost:4131/contact?name=joe`
    then the `url` parameter will have the value "/contact?name=joe". (so the schema and 
    authority will not be included, but the full path, any query, and any anchor will be included)

    This function is called each time another program/computer makes a request to this website.
    The URL represents the requested file.

    This function should return a string.
    """

    # This gets both the path, anchor, and query in a small amount of code
    # Will still work even if query and anchor aren't in the url
    path = url
    query = anchor = None
    if '#' in url:
        path, anchor = url.split("#")
    if '?' in url:
        path, query = filepath.split("?")
    print(f"filepath: {path},  query: {query}, anchor: {anchor}")

    # Take the path and find the respective file
    if path == "/" or path == "/main":
        filepath = MAIN_PAGE
    elif path == "/gallery":
        filepath = LISTINGS_PAGE
    elif path == "/listing/1":
        filepath = "static/html/listing_example.html"
    else:
        filepath = NOT_FOUND_404_PAGE
   
    # Read the html code and return it
    file = open(filepath)
    html = file.read()
    file.close()

    return html

# You shouldn't need to change content below this. It would be best if you just left it alone.

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Call the student-edited server code.
        message = server(self.path)
        
        # Convert the return value into a byte string for network transmission
        if type(message) == str:
            message = bytes(message, "utf8")

        # prepare the response object with minimal viable headers.
        self.protocol_version = "HTTP/1.1"
        # Send response code
        self.send_response(200)
        # Send headers
        # Note -- this would be binary length, not string length
        self.send_header("Content-Length", len(message))
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        # Send the file.
        self.wfile.write(message)
        return

def run():
    PORT = 4131
    print(f"Starting server http://localhost:{PORT}/")
    server = ('', PORT)
    httpd = HTTPServer(server, RequestHandler)
    httpd.serve_forever()
run()

# while (1):
#     url = "/test/path?test#hello"
#     filepath = url
#     query = anchor = None
#     if '#' in url:
#         filepath, anchor = url.split("#")
#     if '?' in url:
#         filepath, query = filepath.split("?")
#     print(filepath, query, anchor)
#     input()