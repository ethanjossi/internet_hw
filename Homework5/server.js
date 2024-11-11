const express = require('express');
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({extended: false}));
app.use('/css', express.static('resources/css'));
app.set('views', 'templates');
app.set('view engine', 'pug');

// CONSTANTS
const port = 4131;

// GET REQUESTS
// app.get(["/", "/main"], (req, res) => {
    
// });

// app.get("/css/main.css", (req, res) => {
//     res.send("resources/css/main.css");
// });

// POST REQUESTS

// DELETE REQUESTS

app.listen(port, () => {
    console.log(`Auction server listening on port ${port}`);
});