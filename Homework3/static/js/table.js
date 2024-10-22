async function loadListings(event) {
    // event.preventDefault()
    try {
        const query = document.getElementById("query").value;
        const category = document.getElementById("category").value;
        const fetch_url = `/json/listings.json?query=${query}&category=${category}`;
        const data = await fetch(fetch_url);
        const listings = await data.json();
        const table = document.getElementById("table_entries");
        listings.forEach(element => {
            const entry = document.createElement("tr");
            entry.classList.add("listingEntry");
            entry.innerHTML = `
                <td>
                    <a href="/listing/${element.id}">${element.title}</a>
                </td>
                <td>${element.bids.length}</td>
                <td>${element.bids[0].bidAmount}</td>
                <td>${element.endDate}</td>`;
            table.appendChild(entry)
        });
    } catch (error) {
        console.error("There was an error fetching the listings", error);
    }
}

// Add an event listener for the search button
// create a search function that parses the search parameters and passes them
// to the loadListings() function which then reloads the page. 

loadListings();
document.getElementById("searchListings").addEventListener("submit", loadListings);