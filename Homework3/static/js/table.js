function calc_time_difference(endTime) {
    const now = new Date();
    let difference = Math.floor((endTime - now) / 1000);
    // Check if the auction ended
    if (difference <= 0) {
        return "Auction Ended";
    }
    const days = Math.floor(difference/86400);
    difference = difference - days*86400;
    const hours = Math.floor(difference/3600);
    difference = difference - hours*3600;
    const minutes = Math.floor(difference/60);
    difference = difference - minutes*60;
    const seconds = difference;

    return `${days}d, ${hours}h, ${minutes}m, ${seconds}s`;
}

function update_auction_times() {
    const table_rows = document.querySelectorAll(".listingEntry");
    for (let i = 0; i < table_rows.length; i++) {
        const timeCell = table_rows[i].cells[3];
        const endTime = new Date(auction_entries[i]);
        timeCell.textContent = calc_time_difference(endTime);
    }
}

function setup_event_listeners() {
    const table_rows = document.querySelectorAll(".listingEntry");
    const image = document.getElementById("imageURL");
    const description = document.getElementById("description");
    table_rows.forEach(entry => {
        entry.addEventListener('mouseenter', () => {
            const imageURL = entry.getAttribute("data-image");
            const descriptionText = entry.getAttribute("data-description");
            image.src = imageURL;
            image.hidden = false;
            description.textContent = descriptionText;
            description.hidden = false;
        })
    });

    // This is for the border for the div
    const galleryDiv = document.querySelector('.gallery');
    const previewDiv = document.querySelector('.preview');
    galleryDiv.addEventListener('mouseenter', () => {
        previewDiv.style.border = '10px solid black'; 
        previewDiv.style.borderRadius = '1em';
    });
}

// Set up the event listeners for the preview
setup_event_listeners();

// Store all the times initially
let auction_entries = []
const auction_end_times = document.querySelectorAll(".listingEntry");
auction_end_times.forEach(entry => {
    const timeCell = entry.cells[3];
    auction_entries.push(timeCell.textContent);
})

// Interval that updates the auction times every second
setInterval(update_auction_times, 1000);