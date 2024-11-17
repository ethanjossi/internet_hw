const express = require('express');
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({extended: false}));
app.use('/css', express.static('resources/css'));
app.use('/images', express.static("resources/images"));
app.use('/js', express.static("resources/js"));
app.set('views', 'templates');
app.set('view engine', 'pug');

// CONSTANTS
const port = 4131;
let listings = require("./resources/json/listings.json");
let id_counter = 4;

// GET REQUESTS
app.get(["/", "/main"], (req, res) => {
    res.render("main.pug");
});

app.get(["/gallery", "/listings"], (req, res) => {
    res.render("listings.pug", {listings});
});

app.get("/listing/:id", (req, res) => {
    const id = parseInt(req.params.id);
    const listing = listings.find(item => item.id == id);
    if (listing) {
        res.render("viewListing.pug", {listing});
    } else {
        res.status(404).render("404.pug", {message: "Listing not found"});
    }
})

app.get("/404", (req, res) => {
    res.status(404);
    res.render("404.pug", {message: "Page Not Found"});
});

app.get("/create", (req, res) => {
    res.render("create.pug");
});

app.get("/createFail", (req, res) => {
    res.render("createFail.pug");
});

app.get("/createSuccess", (req, res) => {
    res.render("createSuccess.pug");
});

// POST REQUESTS
app.post("/create", (req, res) => {
    // console.log(req.body);
    if (check_new_listing(req.body)) {
        const id = add_listing(req.body);
        res.status(303);
        res.set("Location", `/listing/${id}`);
        res.render("createSuccess.pug");
    } else {
        res.status(400);
        res.render("createFail.pug");
    }
});

app.post("/api/place_bid", (req, res) => {
    // console.log(req.body);
    const status = check_new_bid(req.body);
    res.status(status);
    if (status === 201) {
        const listing = add_bid(req.body);
        res.json(listing.bids);
    } else if (status == 409) {
        const listing = get_listing(req.body.listingId)
        res.json(listing.bids);
    } else if (status == 400) {
        res.send("/api/place_bid - client error");
    } else {
        res.status(500);
        res.send("There was a server error");
    }
});

// DELETE REQUESTS
app.delete("/api/delete_listing", (req, res) => {
    const status = check_delete_listing(req.body);
    res.status(status);
    if (status === 204) {
        const id = req.body.listingId;
        delete_listing(id);
        res.send("Listing successfully deleted");
    } else if (status === 400) {
        res.send("Client error in deleting listing");
    } else if (status === 404) {
        res.send("Delete listing - listing id not found");
    } else {
        res.status(500);
        res.send("There was a server error");
    }
})

// Helper functions
function get_listing(id) {
    if (id < 0) {
        return null;
    }
    for (let listing of listings) {
        if (listing.id == id) {
            return listing;
        }
    }
    return null;
}

function check_delete_listing(json_data) {
    // Check all keys are present
    if (!("listingId" in json_data)) {
        console.log("Bad POST /api/delete_listing request - missing key in body");
        return 400;
    }
    // Check that the listing id is a number and is valid
    if (! Number.isInteger(json_data.listingId)) {
        console.log("Bad POST /api/delete_listing request - listing id is not an integer");
        return 400;
    }
    const listing = get_listing(json_data.listingId);
    if (listing === null) {
        console.log("Bad POST /api/delete_listing request - invalid listing id");
        return 404;
    }
    return 204;
}

function delete_listing(id) {
    const index = listings.indexOf(get_listing(id));
    listings.splice(index, 1);
}

function check_new_bid(bid) {
    // Check that all the keys are present
    if (!("listingId" in bid && "bidderName" in bid && "bidAmount" in bid && "comment" in bid)) {
        console.log("Bad POST /api/place_bid request - missing key in body");
        return 400;
    }
    // Check that the listing id is a number and is valid
    if (! Number.isInteger(bid.listingId)) {
        console.log("Bad POST /api/place_bid request - listing id is not an integer");
        return 400;
    }
    const listing = get_listing(bid.listingId);
    if (listing === null) {
        console.log("Bad POST /api/place_bid request - invalid listing id");
        return 404;
    }
    // Check the bid amount is an int or float
    if (typeof(bid.bidAmount) !== "number") {
        console.log("Bad POST /api/place_bid request - bidAmount is not a number");
        return 400;
    }
    // check that the bid amount is greater than the largest bid
    if (bid.bidAmount <= listing.topBid) {
        console.log("Bad POST /api/place_bid request - bid amount is not greater than largest");
        return 409;
    }
    return 201;
}

function add_bid(bid) {
    let listing;
    try {
        listing = get_listing(bid.listingId);
        delete bid.listingId;
        listing.bids.unshift(bid);
        listing.numBids++;
        listing.topBid = bid.bidAmount;
    } catch {
        console.log("Server 500 error for /api/place_bid when adding new bid");
    }
    return listing;
}

function check_new_listing(listing) {
    // Check that all the keys are present
    if (!("title" in listing && "imageURL" in listing && "description" in listing && "category" in listing && "otherCategory" in listing && "endDate" in listing)) {
        console.log("Bad post /create request - missing key in body");
        return false;
    }
    // Check if the sale date is valid
    const saleRegex = /^\d{4}-\d{2}-\d{2}$/;
    const saleDate = listing.endDate;
    if (!saleRegex.test(saleDate)) {
        console.log("Bad POST /create request - sale date not in expected format");
        return false;
    }
    const year = parseInt(saleDate.substring(0, 4));
    const month = parseInt(saleDate.substring(5, 7));
    const day = parseInt(saleDate.substring(8, 10));
    if (!(0 < year && 1 <= month && month <= 12 && 1 <= day && day <= 31)) {
        console.log("Bad POST /create request - sale date not valid");
        return false;
    }
    // Check that otherCategory is correct
    if (listing.category === "other" && listing.otherCategory === "") {
        console.log("Bad post /create request - otherCategory selected but no text present");
        return false;
    }
    // Check if the Url is a valid url
    // const urlRegex = /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/[^\s]*)?$/;
    // if (!urlRegex.test(listing.url)) {
    //     console.log("Bad POST /create request - url is not a valid url");
    //     return false;
    // }
    // if all checks return true
    return true;
}

function add_listing(listing) {
    try {
        if (listing.category == "other") {
            listing.category = listing.otherCategory;
        }
        delete listing.otherCategory;
        listing.id = id_counter++;
        listing.topBid = 0;
        listing.numBids = 0;
        listing.bids = [];
        listings.push(listing);
    } catch {
        console.log("Server 500 /create error when attempting to add the new listing");
    }
    return listing.id;
}

// Default 404 not found
app.all("*", (req, res) => {
    res.status(404).render("404.pug", {message: "Page not Found"});
});

app.listen(port, () => {
    console.log(`Auction server running on http://localhost:${port}`);
});