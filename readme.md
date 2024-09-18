# WeHelp Personal Project 1 - Taipei Day Trip

Last updated on: 2024/09/18

## Overview

![img1_small](https://github.com/user-attachments/assets/c6351835-46dd-404e-b0af-99ccd034d12b) ![img2_small](https://github.com/user-attachments/assets/c67d3ab8-6b4a-4c20-af03-c9842f516eb1)

Taipei Day Trip (url) is a E-commerce website for day trip packages.

Using Python FastAPI as back-end, HTML / CSS / vanilla JS as front-end and MySQL as the database,\
this website is deployed and hosted on AWS EC2.

This is a portfolio project as part of the WeHelp Bootcamp Program.

## Description

Using this website, users can:
1. Browse from a catalog of attractions.
2. Search by keyword for attractions.
3. Filter by MRT station by clicking on desired MRT station on the scroll bar.
4. Read description and browse pictures of an attraction by clicking on desired attraction.

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

FastAPI auto-generated SwaggerUI API documentation can be accessed at /docs(url).

A brief summary is also shown below:

### MRT: For obtaining all Taipei MRT station data.

1. #### GET /api/mrts
- Returns all MRT stations in the current database, sorted by number of nearby attractions (appearance frequency) in descending order.

### Attractions: For obtaining all Taipei attraction data.

1. #### GET /api/attractions 

- Returns the Nth page of data matching the input page number and keyword(optional).

2. #### GET /api/attractions/{attractionId}

- Returns attraction data by attraction ID.

### Users: For user creation and authentication.

1. #### POST /api/user

- Creates a new user.

2. #### PUT /api/user/auth

- Signs in a user to the system. Returns a JWT token if successfully signed-in.

3. #### GET /api/user/auth

- Verifies the JWT token for currently signed-in user.
- Needs authorizaion (Required header: {Authorization: "Bearer ${JWT token}"}).

### Booking: For booking(shopping cart) management.

1. #### GET /api/booking

- Returns the user's current booking(shopping cart).
- Needs authorizaion. 

2. #### POST /api/booking

- Adds an item to the user's booking(shopping cart).
- Needs authorizaion. 

3. #### DELETE /api/booking

- Deletes the user's current booking(shopping cart).
- Needs authorizaion. 

### Order: For placing and checking status of orders.

1. #### POST /api/orders

- Places an order using order details and a TayPay prime. Returns the order number if successful.
- Needs authorizaion. 

2. #### GET /api/orders/{orderNumber}

- Returns the order details and payment status of the provided order number.
- Needs authorizaion. 

## Development Notes

Updates and miscellaneous notes are logged and updated here.

Currently there are no notes!

Last updated on: 2024/09/18