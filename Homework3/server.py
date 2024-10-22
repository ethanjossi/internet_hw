from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import json
import copy
from utils import filepaths, BID_TEMPLATE, LISTING_PAGE, TABLE_TEMPLATE, escape_html, unescape_url

# PUT YOUR GLOBAL VARIABLES AND HELPER FUNCTIONS HERE.
# Load all the listings from the json file
with open("static/json/listings.json", "r") as file:
    listings = json.load(file)


def parse_id(id=None):
    json_data = [listing for listing in listings if listing['id'] == id]
    return json.dumps(json_data, indent=4)
    

def parse_query_category(query=None, category=None):
    json_data = [listing for listing in listings
        if (query is None or query.lower() in listing['title'].lower()) and 
           (category is None or category.lower() == listing['category'].lower())
    ]
    return json.dumps(json_data, indent=4)

def parse_query_parameters(response):
    # If ? at beginning, remove it
    if response.startswith("?"):
        response = response[1:]
    # Split the query string into key-value pairs
    key_values = response.split("&")
    # Initialize a dictionary to store parsed parameters
    query_dict = {}
    # Iterate over each key-value pair
    # Split the pair by '=' to separate key and value
    for pair in key_values:
        key, value = pair.split("=")
        key = unescape_url(key)
        value = unescape_url(value)
        query_dict[key] = value
    return query_dict

# Provided function -- converts numbers like 42 or 7.347 to "$42.00" or "$7.35"
def typeset_dollars(number):
    return f"${number:.2f}"


def get_listing(id: int) -> dict:
    """
    Gets a listing associated with the given id from the listings
    Returns None if the listing with the id doesn't exist
    
    Parameters:
        id (int): the ID of the listing
    
    Returns:
        dict: the dictionary of the listing
    """
    if id < 0:
        return None
    for dict in listings:
        if dict["id"] == id: # We found that the ID exists
            return dict
    return None


def is_valid_id(id: int) -> bool:
    """
    Checks if an ID exists in the listings
    
    Parameters:
        id (int): an ID of a listing
    
    Returns:
        bool: whether the id exists
    """
    if id < 0:
        return False
    return any(entry.get("id") == id for entry in listings)

def get_filepath(path: str) -> str:
    """
    Figures out the correct file to fetch
    If the file does not exist, returns 404 filepath
    
    Parameters:
        path (str): the path to check
    
    Returns:
        str: the filepath for the server to fetch the html
    """
    global filepaths
    filepath = filepaths.get(path, "static/html/404.html")
    return filepath

def server_GET(url: str) -> tuple[str | bytes, str, int]:
    """
    url is a *PARTIAL* URL. If the browser requests `http://localhost:4131/contact?name=joe`
    then the `url` parameter will have the value "/contact?name=joe". (so the schema and
    authority will not be included, but the full path, any query, and any anchor will be included)

    This function is called each time another program/computer makes a request to this website.
    The URL represents the requested file.

    This function should return three values (string or bytes, string, int) in a list or tuple. The first is the content to return
    The second is the content-type. The third is the HTTP Status Code for the response
    """
    # YOUR CODE GOES HERE!
    # This gets both the path, anchor, and query in a small amount of code
    # Will still work even if query and anchor aren't in the url
    path = url
    query = anchor = None
    if '#' in url:
        path, anchor = url.split("#")
    if '?' in url:
        path, query = path.split("?")
    # print(f"filepath: {path},  query: {query}, anchor: {anchor}")

    filepath = get_filepath(path)
    send_data = mime = ""
    http_status = 200
    # Images
    if filepath.startswith("static/images/"):
        print(f"requesting image {filepath}")
        with open(filepath, "rb") as img:
            send_data = img.read()
        mime = "image/jpeg"
    # CSS
    elif filepath.startswith("static/css"):
        with open(filepath) as file:
            send_data = file.read()
        mime = "text/css"
    # JS
    elif filepath.startswith("static/js"):
        with open(filepath) as file:
            send_data = file.read()
        mime = "text/javascript"
    # JSON
    elif filepath.startswith("static/json"):
        query_params = parse_query_parameters(query)
        # If gallery
        if "category" in query_params and "query" in query_params:
            if query_params["category"] == "all":
                query_params["category"] = None
            if query_params["query"] == "":
                query_params["query"] = None
            send_data = parse_query_category(query_params["query"], query_params["category"])
        # else listing
        else:
            send_data = parse_id(query_params["id"])
        mime = "application/json"
    # All other pages
    else:
        with open(filepath) as file:
            send_data = file.read()
        mime = "text/html"
    print(f"webpath: {path}     filepath: {filepath}      mime: {mime}")
    # ADD IN CHARSET
    return send_data, mime, http_status


def server_POST(url: str, body: str) -> tuple[str | bytes, str, int]:
    """
    url is a *PARTIAL* URL. If the browser requests `http://localhost:4131/contact?name=joe`
    then the `url` parameter will have the value "/contact?name=joe". (so the schema and
    authority will not be included, but the full path, any query, and any anchor will be included)

    This function is called each time another program/computer makes a POST request to this website.

    This function should return three values (string or bytes, string, int) in a list or tuple. The first is the content to return
    The second is the content-type. The third is the HTTP Status Code for the response
    """
    pass


# You shouldn't need to change content below this. It would be best if you just left it alone.


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the content-length header sent by the BROWSER
        content_length = int(self.headers.get("Content-Length", 0))
        # read the data being uploaded by the BROWSER
        body = self.rfile.read(content_length)
        # we're making some assumptions here -- but decode to a string.
        body = str(body, encoding="utf-8")

        message, content_type, response_code = server_POST(self.path, body)

        # Convert the return value into a byte string for network transmission
        if type(message) == str:
            message = bytes(message, "utf8")

        # prepare the response object with minimal viable headers.
        self.protocol_version = "HTTP/1.1"
        # Send response code
        self.send_response(response_code)
        # Send headers
        # Note -- this would be binary length, not string length
        self.send_header("Content-Length", len(message))
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        # Send the file.
        self.wfile.write(message)
        return

    def do_GET(self):
        # Call the student-edited server code.
        message, content_type, response_code = server_GET(self.path)

        # Convert the return value into a byte string for network transmission
        if type(message) == str:
            message = bytes(message, "utf8")

        # prepare the response object with minimal viable headers.
        self.protocol_version = "HTTP/1.1"
        # Send response code
        self.send_response(response_code)
        # Send headers
        # Note -- this would be binary length, not string length
        self.send_header("Content-Length", len(message))
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        # Send the file.
        self.wfile.write(message)
        return


def run():
    PORT = 4131
    print(f"Starting server http://localhost:{PORT}/")
    server = ("", PORT)
    httpd = HTTPServer(server, RequestHandler)
    httpd.serve_forever()


run()
