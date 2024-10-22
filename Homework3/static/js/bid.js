async function loadBid() {
    try {
        const bid_num = window.location.pathname.split('/')
        const id = parseInt(bid_num.pop())
        const fetch_url = `http://localhost:4131/json/listings.json?id=${id}`;
        const data = await fetch(fetch_url);
        const listings = await data.json();
        const bid = document.getElementById("table_entries");
        listings.forEach(element => {
    } catch (error) {
        console.error("There was an error fetching the listings", error);
    }
}