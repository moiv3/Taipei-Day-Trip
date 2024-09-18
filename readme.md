# WeHelp Personal Project 1 - Taipei Day Trip

## Overview

![img1_small](https://github.com/user-attachments/assets/c6351835-46dd-404e-b0af-99ccd034d12b) ![img2_small](https://github.com/user-attachments/assets/c67d3ab8-6b4a-4c20-af03-c9842f516eb1)

Taipei Day Trip is a E-commerce website for day trip packages.

Using Python FastAPI as back-end, HTML / CSS / vanilla JS as front-end and MySQL as the database.\
this website is deployed and hosted on AWS EC2.

This is a portfolio project as part of the WeHelp Bootcamp Program.

## Description

Using this website, users can:
1. Browse from a catalog of attractions.
2. Search by keyword for attractions.
3. Filter by MRT station by clicking on desired MRT station on the scroll bar.
4. Read description and browse pictures of an attraction by cliking on desired attraction.

By signing in to the website, in addition to the features above, users can now:
1. Add tour packages to their shopping cart.
2. Confirm and delete contents of the shopping cart.
3. Pay by credit card to finalize the transaction.
(Note: TapPay test environment is used, so no actual transaction is done.)

## Architecture Diagram

The figure below describes the architecture diagram of Taipei Day Trip.\
It is a simple system using 1 AWS EC2 instance and MySQL installed directly in the instance.

![TDT_architeture diagram](https://github.com/user-attachments/assets/5add17a8-8d57-44ec-8c4b-d8424c1e1396)

## APIs

FastAPI auto-generated SwaggerUI API documentation can be accessed at /docs.

A brief summary is also shown below:

### MRT
#### /api/mrts (method: GET)

input parameters: none. 

output: {"data": list[strings]}

Returns all MRT stations in the current database, sorted by number of nearby attractions (appearance frequency) in descending order.


### Attractions
#### /api/attractions (method: GET)

input parameters(query string): 

1. page: returns the nth page of data matching the input page number.
2. keyword: if used, returns data only if attraction name partially matches keyword or MRT station exactly matches keyword. if not used, returns all data.


Returns attractions based on query strings.

Returns maximum of 12 Entries per page with page number starting from 0. 

If there is a next page, page number of next page will also be returned as nextPage: next_page_number. If not, returns nextPage: null.

#### /api/Attraction/{attractionId} (method: GET)

input parameters(URL): 
attractionId: returns data for the requested attraction ID.

output: {"data": list[Attractions]}

### Users
#### /api/user (method: POST)
Creates a new user.

Request body:
{
  "name": "Your Name Here",
  "email": "your@email.net",
  "password": "somepassword"
}

Output:
Successful registration: server responses with {"ok": true}.
Unsuccessful registration: server responses with {"error": true, "message": error message}.

## Development Notes

Updates and miscellaneous notes are logged and updated here.

Currently there are no notes:)
