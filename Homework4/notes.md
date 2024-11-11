## Building the api for placing new bids

#### Back-end

- create a function to check that content type header is present and matches.
    - the function will have parameters (dict: headers, string: content-type)
- parse body function:
- check that the body when a POST request is sent is not empty
- parse the JSON and check that there was not an error parsing it
- check isinstance(json_data, dict) to make sure it got parsed as a dictionary
- check all properties are present
    - extra properties should be ignored
    - check bidder name is string
    - check bid amount is number
        - check bid amount is greater than previous
        - if not return 409
    - listing id is real
        - if listing id is not found return 404
    - return 400 error for all
- add the bid, can reuse function from HW3
- return in the body of the response all of the current bids with the one just added also present

#### Front-end

