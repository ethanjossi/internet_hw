from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib  # Only for parse.unquote and parse.unquote_plus.
import json
import base64
from typing import Union, Optional
import re
from datetime import datetime
import time
# If you need to add anything above here you should check with course staff first.

# Load all the listings from the json file
with open("static/json/listings.json", "r") as file:
    listings = json.load(file)

# PUT YOUR GLOBAL VARIABLES AND HELPER FUNCTIONS HERE.
LISTING_PAGE = "listing_page.html"
TABLE_TEMPLATE = """
<tr class="listingEntry" data-image="{imageURL}" data-description="{description}" data-listing-id="{listing_id}">
    <td>
        <a href="{URL}">{title}</a>
    </td>
    <td>{num_bids}</td>
    <td>${top_bid}</td>
    <td>{endDate}</td>
    <td><button class="delete_listing">delete</button></td>
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
        "/js/table.js": "static/js/table.js",
        "/create": "static/html/create.html",
        "/api/place_bid": "",
        "/api/delete_listing": ""
    }

# Provided helper function. This function can help you implement rate limiting
rate_limit_store = []


def pass_api_rate_limit() -> tuple[bool, int | None]:
    """This function will keep track of rate limiting for you.
    Call it once per request, it will return how much delay would be needed.
    If it returns 0 then process the request as normal
    Otherwise if it returns a positive value, that's the number of seconds
    that need to pass before the next request"""
    from datetime import datetime, timedelta

    global rate_limit_store
    # you may find it useful to change these for testing, such as 1 request for 3 seconds.s
    RATE_LIMIT = 4  # requests per second
    RATE_LIMIT_WINDOW = 10  # seconds
    # Refresh rate_limit_store to only "recent" times
    rate_limit_store = [
        time
        for time in rate_limit_store
        if datetime.now() - time <= timedelta(seconds=RATE_LIMIT_WINDOW)
    ]
    if len(rate_limit_store) >= RATE_LIMIT:
        return (
            RATE_LIMIT_WINDOW - (datetime.now() - rate_limit_store[0]).total_seconds()
        )
    else:
        # Add current time to rate_limit_store
        rate_limit_store.append(datetime.now())
        return 0


def escape_html(str):
    # this i s a bare minimum for hack-prevention.
    # You might want more.
    str = str.replace("&", "&amp;")
    str = str.replace('"', "&quot;")
    str = str.replace("<", "&lt;")
    str = str.replace(">", "&gt;")
    str = str.replace("'", "&#39;")
    return str


def unescape_url(url_str):
    import urllib.parse

    # NOTE -- this is the only place urllib is allowed on this assignment.
    return urllib.parse.unquote_plus(url_str)


def parse_query_parameters(response) -> dict:
    if response is None:
        return {}
    pairs = response.split("&")
    pairs2 = []
    for pair in pairs:
        if pair.count("=") == 1 and pair.split("=")[0] != "":
            pairs2.append(pair)
    pairs = pairs2
    parsed_params = {}

    for pair in pairs:
        key = unescape_url(pair.split("=")[0])
        value = unescape_url(pair.split("=")[1])
        parsed_params[key] = value

    return parsed_params

def parse_body(body: str) -> tuple[dict, int]:
    """
    This method parses the body and checks that the body is not empty
    if there is any error parsing the json or the body is empty, None
    will be returned.
    Parameters:
        body: string - body of the request
    Returns:
        json object - the parsed json"""
    if body == "" or body is None:
        return None, 400
    try:
        json_data = json.loads(body)
    except:
        return None, 400
    if not isinstance(json_data, dict):
        return None, 400
    return json_data, None

    

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
            table_entries += TABLE_TEMPLATE.format(imageURL=entry["imageURL"], description=entry["description"], listing_id=entry["id"], URL=url, title=entry["title"], num_bids=len(entry["bids"]), top_bid=bid_amount, endDate=entry["endDate"])
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

def delete_listing(body: dict) -> int:
    """
    Deletes a listing. Returns an integer that represents
    the status code of the deletion.
    Parameters:
        body: dictionary - a dict containing the listing id
    Returns:
        int: the status code of the deletion"""
    # Check all keys required are present
    required_keys = ["listing_id"]
    if not all(key in body for key in required_keys):
        return 400
    # Check that the listing ID exists
    if get_listing(body["listing_id"]) is None:
        return 404
    # Check the listing id is an int
    if type(body["listing_id"]) is not int:
        return 400
    # Delete the listing, return 204
    for idx, listing in enumerate(listings):
        if listing.get("id") == body.get("listing_id"):
            del listings[idx]
    return 204


def add_new_bid(queryParams: dict) -> tuple[int, str]:
    # Check all required keys are present
    required_keys = ["listing_id", "bidder_name", "bid_amount", "comment"]
    if not all(key in queryParams for key in required_keys):
        return 400, None
    # Check that the values are the types they should be
    if not (isinstance(queryParams["bidder_name"], str) and isinstance(queryParams["bid_amount"], int) and isinstance(queryParams["listing_id"], int)):
        return 400, None
    # Check that the listing ID exists
    if get_listing(queryParams["listing_id"]) is None:
        return 400, None
    # Check that the bid is greater than the max bid
    id = queryParams.get("listing_id")
    if queryParams["bid_amount"] <= get_max_bid(id):
        return 409, None
    # Add the bid to the listing
    bid = {}
    bid["bidderName"] = queryParams.get("bidder_name")
    bid["bidAmount"] = int(queryParams.get("bid_amount"))
    bid["comment"] = queryParams.get("comment")
    get_listing(id).get("bids").insert(0, bid)
    return 201, bid["bidderName"]

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

def check_headers(headers: dict) -> bool:
    if "Content-Type" in headers and (headers.get("Content-Type") == "application/json" or headers.get("Content-Type") == "application/x-www-form-urlencoded"):
        return True
    return False

# The method signature is a bit "hairy", but don't stress it -- just check the documentation below.
# NOTE some people's computers don't like the type hints. If so replace below with simply: `def server(method, url, body, headers)`
# The type hints are fully optional in python.
def server(
    request_method: str,
    url: str,
    request_body: Optional[str],
    request_headers: dict[str, str],
) -> tuple[Union[str, bytes], int, dict[str, str]]:
    """
    `method` will be the HTTP method used, for our server that's GET, POST, DELETE, and maybe PUT
    `url` is the partial url, just like seen in previous assignments
    `body` will either be the python special `None` (if the body wouldn't be sent (such as in a GET request))
         or the body will be a string-parsed version of what data was sent.
    headers will be a python dictionary containing all sent headers.

    This function returns 3 things:
    The response body (a string containing text, or binary data)
    The response code (200 = ok, 404=not found, etc.)
    A _dictionary_ of headers. This should always contain Content-Type as seen in the example below.
    """
    response_headers = {}

    path = url
    query = anchor = None
    if '#' in url:
        path, anchor = url.split("#", 1)
    if '?' in url:
        path, query = path.split("?", 1)
    # print(f"filepath: {path},  query: {query}, anchor: {anchor}")

    filepath = get_filepath(path)
    mime = None
    response_body = ""
    content_type = "text/html"
    status_code = 200

    # Check valid METHOD
    if request_method not in ["GET", "POST", "DELETE"]:
        return "", 405, {"Content-Type": "text/html; charset=utf-8"}
    # Return 404 if not valid path
    if filepath == "static/html/404.html":
        with open(filepath) as file:
            response_body = file.read()
        return response_body, 404, {"Content-Type": "text/html; charset=utf-8"}
    # Check Rate limiting, immediately return 429
    if path.startswith("/api/"):
        wait_time = pass_api_rate_limit()
        if wait_time != 0:
            return "", 429, {"Content-Type": "text/html; charset=utf-8",
                            "Retry-After": wait_time}


    if request_method == "GET":
        query_params = parse_query_parameters(query)
        # Single Listing
        if filepath == LISTING_PAGE:
            number = path[9:]
            response_body = render_listing(get_listing(int(number)))
            mime = "text/html"
        # Images
        elif filepath.startswith("static/images/"):
            with open(filepath, "rb") as img:
                response_body = img.read()
            mime = "image/jpeg"
        # CSS
        elif filepath.startswith("static/css"):
            with open(filepath) as file:
                response_body = file.read()
            mime = "text/css"
        # Gallery Page
        elif filepath == "static/html/listings.html":
            # Check that category and query exist, if not, add them. 
            if "category" not in query_params or "query" not in query_params:
                query_params["category"] = "all"
                query_params["query"] = ""
            # Set them to None if they are for any value
            if query_params["category"] == "all":
                query_params["category"] = None
            if query_params["query"] == "":
                query_params["query"] = None
            response_body = render_gallery(query=query_params["query"], category=query_params["category"])
            mime = "text/html"
        # Javascript
        elif filepath.startswith("static/js"):
            with open(filepath) as file:
                response_body = file.read()
            mime = "text/javascript"
        # Default - All other pages
        else:
            with open(filepath) as file:
                response_body = file.read()
            mime = "text/html"
    elif request_method == "POST":
        query_params = parse_query_parameters(request_body)
        # Create Listing
        if check_headers(request_headers) == False:
            status_code = 400
        elif path == "/create":
            if add_new_listing(query_params):
                status_code = 303
                response_headers["Location"] = "/listing/{}".format(listings[-1].get("id"))
            else:
                status_code = 400
                with open("static/html/create_fail") as file:
                    response_body = file.read()
            mime = "text/html"
        # Place Bid
        elif path == "/api/place_bid":
            json_data, status_code = parse_body(request_body)
            if json_data is not None:
                # Replace bidder name if cookie is present
                if "Cookie" in request_headers:
                    cookies = request_headers["Cookie"].split("=")
                    if cookies[0] == "bidder_name" and len(cookies) == 2:
                        json_data["bidder_name"] = cookies[1]
                status_code, bidder_name = add_new_bid(json_data)
                if status_code == 201 or status_code == 409:
                    response_body = json.dumps(get_listing(json_data["listing_id"]).get("bids"))
            # Set cookie if needed
            if "Cookie" not in request_headers:
                response_headers["Set-Cookie"] = "bidder_name={}; Path=/".format(bidder_name)
            mime = "application/json"
    elif request_method == "DELETE":
        if check_headers(request_headers) == False:
            status_code = 400
        elif path == "/api/delete_listing":
            json_data, status_code = parse_body(request_body)
            if json_data is not None:
                status_code = delete_listing(json_data)

    content_type = "{mime}; charset=utf-8".format(mime=mime)
    response_headers["Content-Type"] = content_type

    print(f"\npath: {path}    filepath: {filepath}    method: {request_method}")
    print(f"status code: {status_code}")
    if request_body is not None:
        print(f"JSON request: {request_body}")

    return response_body, status_code, response_headers


# You shouldn't need to change content below this. It would be best if you just left it alone.


class RequestHandler(BaseHTTPRequestHandler):
    def c_read_body(self):
        # Read the content-length header sent by the BROWSER
        content_length = int(self.headers.get("Content-Length", 0))
        # read the data being uploaded by the BROWSER
        body = self.rfile.read(content_length)
        # we're making some assumptions here -- but decode to a string.
        body = str(body, encoding="utf-8")
        return body

    def c_send_response(self, message, response_code, headers):
        # Convert the return value into a byte string for network transmission
        if type(message) == str:
            message = bytes(message, "utf8")

        # Send the first line of response.
        self.protocol_version = "HTTP/1.1"
        self.send_response(response_code)

        # Send headers (plus a few we'll handle for you)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", len(message))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        # Send the file.
        self.wfile.write(message)

    def do_POST(self):
        # Step 1: read the last bit of the request
        try:
            body = self.c_read_body()
        except Exception as error:
            # Can't read it -- that's the client's fault 400
            self.c_send_response(
                "Couldn't read body as text", 400, {"Content-Type": "text/plain"}
            )
            raise

        try:
            # Step 2: handle it.
            message, response_code, headers = server(
                "POST", self.path, body, self.headers
            )
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response(
                "The server function crashed.", 500, {"Content-Type": "text/plain"}
            )
            raise

    def do_GET(self):
        try:
            # Step 1: handle it.
            message, response_code, headers = server(
                "GET", self.path, None, self.headers
            )
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response(
                "The server function crashed.", 500, {"Content-Type": "text/plain"}
            )
            raise

    def do_DELETE(self):
        # Step 1: read the last bit of the request
        try:
            body = self.c_read_body()
        except Exception as error:
            # Can't read it -- that's the client's fault 400
            self.c_send_response(
                "Couldn't read body as text", 400, {"Content-Type": "text/plain"}
            )
            raise

        try:
            # Step 2: handle it.
            message, response_code, headers = server(
                "DELETE", self.path, body, self.headers
            )
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response(
                "The server function crashed.", 500, {"Content-Type": "text/plain"}
            )
            raise


def run():
    PORT = 4131
    print(f"Starting server http://localhost:{PORT}/")
    server = ("", PORT)
    httpd = HTTPServer(server, RequestHandler)
    httpd.serve_forever()


run()
