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
// app.post("/create", (req, res) => {
// });

// DELETE REQUESTS

// Helper functions
function check_new_listing(listing) {
    // Check that all the keys are present
    const reqValues = ["title", "url", "description", "category", "otherCategory", "saleDate"];
    if (!reqValues.every(key => listing.hasOwnProperty(key))) {
        return false;
    }
    // Check if the sale date is valid
    const saleRegex = /^\d{4}-\d{2}-\d{2}$/;
    const saleDate = listing.saleDate;
    if (!saleRegex.test(saleDate)) {
        return false;
    }
    const year = parseInt(saleDate.substring(0, 4));
    const month = parseInt(saleDate.substring(5, 7));
    const day = parseInt(saleDate.substring(8, 10));
    if (!(0 < year && 1 <= month && month <= 12 && 1 <= day && day <= 31)) {
        return false;
    }
    // Convert the sale date
    // Check if the category is other, if so make sure other not missing
    if (listing.category === "other" && listing.otherCategory === "") {
        return false;
    }
    // Check if the Url is a valid url
    const urlRegex = /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/[^\s]*)?$/;
    if (!urlRegex.test(listing.url)) {
        return false;
    }
    // if all checks return true
    return true;
}

// Default 404 not found
app.all("*", (req, res) => {
    res.status(404).render("404.pug", {message: "Page not Found"});
});

app.listen(port, () => {
    console.log(`Auction server running on http://localhost:${port}`);
});