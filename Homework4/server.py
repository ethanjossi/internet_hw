from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime

# Load all the listings from the json file
with open("static/json/listings.json", "r") as file:
    listings = json.load(file)

# PUT YOUR GLOBAL VARIABLES AND HELPER FUNCTIONS HERE.
LISTING_PAGE = "listing_page.html"
TABLE_TEMPLATE = """
<tr class="listingEntry" data-image="{imageURL}" data-description="{description}">
    <td>
        <a href="{URL}">{title}</a>
    </td>
    <td>{num_bids}</td>
    <td>${top_bid}</td>
    <td>{endDate}</td>
</tr>"""
BID_TEMPLATE = """
<div class="bid">
    <p><span class="bidder">{bidderName}: </span><span class="amount">{bidAmount}</span></p>
    <p>Comments: {comment}</p>
</div>"""
# Dictionary to find page URLs
filepaths = {
        "/": "static/html/mainpage.html",
        "/main": "static/html/mainpage.html",
        "css": "static/css/main.css",
        "/gallery": "static/html/listings.html",
        "/gallery/search": "static/html/listings.html",
        "/create": "static/html/create.html",
        "/listing/0": LISTING_PAGE,
        "/listing/1": LISTING_PAGE,
        "/listing/2": LISTING_PAGE,
        "/listing/3": LISTING_PAGE,
        "/images/main": "static/images/main.jpg",
        "/images/0": "static/images/0.jpg",
        "/images/1": "static/images/1.jpeg",
        "/images/2": "static/images/2.jpeg",
        "/images/3": "static/images/3.jpg",
        "/main.css": "static/css/main.css",
        "/js/bid.js": "static/js/bid.js",
        "/js/new_listing.js": "static/js/new_listing.js",
        "/js/table.js": "static/js/table.js"
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


def parse_query_parameters(response) -> dict:
    if response is None:
        return {"category": "all", "query": ""}
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


def render_listing(listing) -> str:
    title = listing["title"]
    imageURL = listing["imageURL"]
    description = listing["description"]
    category = listing["category"]
    endDate = listing["endDate"]
    id = listing["id"]
    # Format all the bids
    bids = ""
    for bid in listing["bids"]:
        bids += BID_TEMPLATE.format(bidderName=bid["bidderName"], bidAmount=typeset_dollars(bid["bidAmount"]), comment=bid["comment"])
    if bids == "":
        bids = "<p>Be the first to bid!</p>"
    # Write the html
    with open("static/html/listing_page.html") as f:
        html = f.read()
    html = html.format(title=title, id=id, imageURL=imageURL, description=description, category=category, endDate=endDate, bids=bids)
    return html

def render_gallery(query=None, category=None):
    with open("static/html/listings.html") as f:
        html = f.read()
    # loop over the elements of listings
    table_entries = ""
    for entry in listings:
        if ((query is None) or (query.lower() in entry.get("title").lower())) and ((category is None) or (category == entry.get("category"))):
            # The entry meets the search parameters, add it to the table entries
            url = "/listing/{num}".format(num=entry["id"])
            if entry["bids"] == []:
                bid_amount = 0
            else:
                bid_amount = get_max_bid(entry["id"])
            table_entries += TABLE_TEMPLATE.format(imageURL=entry["imageURL"], description=entry["description"], URL=url, title=entry["title"], num_bids=len(entry["bids"]), top_bid=bid_amount, endDate=entry["endDate"])
    # Format the table entries into the listings page
    if table_entries == "":
        table_entries = "<p>No listings found</p>"
    html = html.format(table_entries=table_entries)
    return html

def add_new_listing(queryParams: dict) -> bool:
    # Check first that all the entries are there
    if ("title" not in queryParams) or ("url" not in queryParams) or ("description" not in queryParams) or ("category" not in queryParams) or ("saleDate" not in queryParams):
        # print(queryParams)
        return False
    # Convert sale date and check if sale date is valid
    year = queryParams.get("saleDate")[0:4]
    month = queryParams.get("saleDate")[5:7]
    day = queryParams.get("saleDate")[8:10]
    sale_date = "{year}-{month}-{day}T14:00:00Z".format(year=year, month=month, day=day)
    year = int(year)
    month = int(month)
    day = int(day)
    if (datetime(year, month, day) < datetime.now()):
        return False
    # Check if category is other, that other is not missing
    if queryParams.get("category") == "other" and queryParams.get("otherCategory") == "":
        return False
    # Add the appropriate listing to the listing dictionary
    new_listing = {}
    new_listing["title"] = queryParams.get("title")
    new_listing["imageURL"] = queryParams.get("url")
    new_listing["description"] = queryParams.get("description")
    if queryParams.get("category") == "other":
        new_listing["category"] = queryParams.get("otherCategory")
    else:
        new_listing["category"] = queryParams.get("category")
    id = listings[-1].get("id") + 1
    new_listing["id"] = id
    new_listing["endDate"] = sale_date
    new_listing["bids"] = []
    listings.append(new_listing)
    filepaths["/listing/{}".format(id)] = LISTING_PAGE
    return True

def add_new_bid(queryParams: dict) -> bool:
    # Check if all the entries are there
    if ("name" not in queryParams) or ("amount" not in queryParams) or ("comment" not in queryParams) or ("bidID" not in queryParams):
        return False
    # Check that the bid is a number, the listing id exists and that it's larger than the current max bid
    if (not queryParams.get("bidID").isdigit()):
        return False
    id = int(queryParams.get("bidID"))
    if (get_listing(id) == None) or (int(queryParams.get("amount")) <= get_max_bid(id)):
        return False
    # Add the bid to the listing
    bid = {}
    bid["bidderName"] = queryParams.get("name")
    bid["bidAmount"] = int(queryParams.get("amount"))
    bid["comment"] = queryParams.get("comment")
    get_listing(id).get("bids").insert(0, bid)
    return True

def get_max_bid(id: int) -> int:
    listing = get_listing(id)
    if not listing.get("bids"): # list is empty
        return 0
    max_bid = max(listing.get("bids"), key=lambda x: x["bidAmount"])
    return max_bid["bidAmount"]

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
    status_code = 200
    # Individual Listing
    if filepath == LISTING_PAGE:
        number = path[9:]
        send_data = render_listing(get_listing(int(number)))
        mime = "text/html"
    # Images
    elif filepath.startswith("static/images/"):
        print(f"requesting image {filepath}")
        with open(filepath, "rb") as img:
            send_data = img.read()
        mime = "image/jpeg"
    # CSS
    elif filepath.startswith("static/css"):
        with open(filepath) as file:
            send_data = file.read()
        mime = "text/css"
    # Listing Page
    elif filepath == "static/html/listings.html":
        query_params = parse_query_parameters(query)
        # Check that category and query exist, if not, add them. 
        if "category" not in query_params or "query" not in query_params:
            query_params["category"] = "all"
            query_params["query"] = ""
        # Set them to None if they are for any value
        if query_params["category"] == "all":
            query_params["category"] = None
        if query_params["query"] == "":
            query_params["query"] = None
        send_data = render_gallery(query=query_params["query"], category=query_params["category"])
        mime = "text/html"
    # Javascript
    elif filepath.startswith("static/js"):
        with open(filepath) as file:
            send_data = file.read()
        mime = "text/javascript"
    # All other pages
    else:
        with open(filepath) as file:
            send_data = file.read()
        mime = "text/html"
    print(f"path: {path} filepath: {filepath}")
    if filepath == "static/html/404.html":
        status_code = 404
    # ADD IN CHARSET
    return send_data, mime, status_code


def server_POST(url: str, body: str) -> tuple[str | bytes, str, int]:
    path = url
    query = anchor = None
    if '#' in url:
        path, anchor = url.split("#")
    if '?' in url:
        path, query = path.split("?")
    print(f"filepath: {path},  query: {query}, anchor: {anchor}")
    print(f"BODY: {body}")

    send_data = mime = ""
    status_code = 200

    if path == "/create":
        query_params = parse_query_parameters(body)
        result = add_new_listing(query_params)
        if result:
            status_code = 201
            with open("static/html/create_success.html") as file:
                send_data = file.read()
        else:
            status_code = 400
            with open("static/html/create_fail.html") as file:
                send_data = file.read()
        mime = "text/html"
    elif path == "/place_bid":
        query_params = parse_query_parameters(body)
        result = add_new_bid(query_params)
        status_code = 201 if result else 400
        send_data = render_listing(get_listing(int(query_params.get("bidID"))))
        mime = "text/html"
    
    return send_data, mime, status_code


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