const placeBidButton = document.getElementById('placeBidButton');
const bidForm = document.querySelector('.newBid');

placeBidButton.addEventListener('click', function() {
    if (bidForm.style.display === 'none' || bidForm.style.display === '') {
        bidForm.style.display = 'flex';
        placeBidButton.textContent = 'Cancel Bid';
    } else {
        bidForm.style.display = 'none';
        placeBidButton.textContent = 'Place Bid';
    }
});

// Code to put the listing id in the hidden form element
const bidnum = parseInt(document.getElementById("listingID").innerText)
const bidID = parseInt(bidnum);

// Put the listing id into the form
const bidIDelem = document.getElementById('bidID');
if (bidIDelem && !isNaN(bidID)) {
    bidIDelem.value = bidID;
} else {
    console.error("There was an error getting the listing id for adding a new bid.");
}

date = document.getElementById("endDate");
date.innerText = "Bid ends: " + new Date(date.innerText.substring(10)).toLocaleDateString();