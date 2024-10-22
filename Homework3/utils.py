# These are helper functions for server.py

LISTING_PAGE = "static/html/listing_page.html"
TABLE_TEMPLATE = """
<tr class="listingEntry">
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
        "/createSuccess": "static/html/create_success.html",
        "/createFail": "static/html/create_fail.html",
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
        "/json/listings.json": "static/json/listings.json",
        "/js/table.js": "static/js/table.js",
        "/js/bid.js": "static/js/table.js"
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

