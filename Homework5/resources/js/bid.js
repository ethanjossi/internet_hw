// Hiding and unhiding the newbid box
const placeBidButton = document.getElementById('placeBidButton');
const bidDiv = document.querySelector('.newBid');

// Code to put the listing id in the hidden form element
const bidnum = parseInt(document.getElementById("listingID").innerText)
const bidID = parseInt(bidnum);

placeBidButton.addEventListener('click', function() {
    if (bidDiv.style.display === 'none' || bidDiv.style.display === '') {
        bidDiv.style.display = 'flex';
        placeBidButton.textContent = 'Cancel Bid';
    } else {
        bidDiv.style.display = 'none';
        placeBidButton.textContent = 'Place Bid';
    }
});

// Fetch code for new bid
const submitBidButton = document.getElementById("submitBidButton");
submitBidButton.addEventListener("click", submit_bid);

async function submit_bid() {
    // get all the data and parse it into a json object
    const json_data = `{
                    "listing_id": ${bidID},
                    "bidder_name": "${document.getElementById("name").value}",
                    "bid_amount": ${document.getElementById("amount").value},
                    "comment": "${document.getElementById("comment").value}"}`;
    // send the json object
    // Repeatedly send until the request is processed
    let retry;
    let response;
    do {
        response = await fetch('/api/place_bid', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: json_data
        });

        retry = response.status === 429;
        if (retry) {
            let wait_time = response.headers["Retry-After"];
            const delay = parseInt(wait_time);
            await new Promise(resolve => setTimeout(resolve, delay));
        }

    } while (retry);

    const json_response = await response.json();
    if (response.status == 201) {
        bidDiv.style.display = 'none';
        placeBidButton.textContent = 'Place Bid';
        document.getElementById("name").value = document.cookie.split('=')[1];
        document.getElementById("amount").value = "";
        document.getElementById("comment").value = "";
        document.getElementById("amount").style.border = "";
        format_bids(json_response);
    } else if (response.status == 409) {
        document.getElementById("amount").style.border = "2px solid red";
    } else {
        alert("There has been a server error");
    }
}

function format_bids(json_bids) {
    const bidContainer = document.querySelector(".bids");
    // Remove all the bids
    document.querySelectorAll(".bid").forEach(element => element.remove());
    // Add in the new bids
    json_bids.forEach(bid => {
        const bidDiv = document.createElement('div');
        bidDiv.classList.add('bid');
        bidDiv.innerHTML = `
            <p><span class="bidder">${bid.bidderName}: </span><span class="amount">$${bid.bidAmount}</span></p>
            <p>Comments: ${bid.comment}</p>
        `;
        bidContainer.appendChild(bidDiv);
    });
}


// Put the listing id into the form
const bidIDelem = document.getElementById('bidID');
if (bidIDelem && !isNaN(bidID)) {
    bidIDelem.value = bidID;
} else {
    console.error("There was an error getting the listing id for adding a new bid.");
}

date = document.getElementById("endDate");
date.innerText = "Bid ends: " + new Date(date.innerText.substring(10)).toLocaleDateString();