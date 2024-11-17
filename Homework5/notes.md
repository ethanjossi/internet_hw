## Don't forget
* Check previous homeworks for lost points and make sure you fix these things
    * Fix tables size changing as the time information changes
    * Ensure client-side validation that the bid amount is larger than the largest current bid
* Remove image width attribute on viewListing.pug (or at least check that this passes an HTML validator)


## Upgrades to server
* Remove the other category when passed in the POST request - this can just be category and the javascript can parse it on the client side so that if otherCategory is selected it will send the new one created
* Respond with error message and type of error message when there is an error - this way server will display what the error is.