from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import json

# Load all the listings from the json file
with open("static/json/listings.json", "r") as file:
    listings = json.load(file)

# PUT YOUR GLOBAL VARIABLES AND HELPER FUNCTIONS HERE.
# Dictionary to find page URLs
filepaths = {
        "/": "static/html/mainpage.html",
        "/main": "static/html/mainpage.html",
        "css": "static/css/main.css"
    }

def escape_html(str):
    str = str.replace("&", "&amp;")
    str = str.replace('"', "&quot;")
    str = str.replace("'", "&#39;")
    str = str.replace("<", "&lt;")
    str = str.replace(">", "&gt;")

    return str

# Use this function only after splitting the paramters & anchor from the URL
def unescape_url(url_str):
    import urllib.parse

    # NOTE -- this is the only place urllib is allowed on this assignment.
    return urllib.parse.unquote_plus(url_str)


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
        query_dict[key] = value
    return query_dict


def render_listing(listing):
    title = listing["title"]
    imageURL = listing["imageURL"]
    description = listing["description"]
    category = listing["category"]
    endDate = listing["endDate"]
    with open("static/html/listing_page.html") as f:
        html = f.read()
    html = html.format(title=title, imageURL=imageURL, description=description, category=category, endDate=endDate)
    return html

def render_gallery(query, category):
    pass


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
    filepath = str()
    

def server(url):
    # This gets both the path, anchor, and query in a small amount of code
    # Will still work even if query and anchor aren't in the url
    path = url
    query = anchor = None
    if '#' in url:
        path, anchor = url.split("#")
    if '?' in url:
        path, query = path.split("?")
    # print(f"filepath: {path},  query: {query}, anchor: {anchor}")

    # Check the path and find the respective file
    # Check or get the correct listing
    if path.startswith("/listing/"):
        number = path[9:]
        if number.isdigit() and is_valid_id(int(number)): # Check if the listing id is valid
            # Valid ID number, so render listing
            html = render_listing(get_listing(int(number)))
        else:
            filepath = "static/html/404.html"
    else:
        global filepaths
        filepath = filepaths.get(path, "static/html/404.html")
        with open(filepath) as file:
            html = file.read()

    return html, "text/html"


# You shouldn't need to change content below this. It would be best if you just left it alone.
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Call the student-edited server code.
        message, content_type = server(self.path)

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
