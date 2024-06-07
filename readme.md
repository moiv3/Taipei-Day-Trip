# WeHelp Stage2 Project
## **This project is still in progress!!**

This is the readme file for Brian's WeHelp Stage2 Project.

## Site description

A e-commerce website for day trip packages.

## APIs

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

## Development Notes

### Week 1

#### 1. json parsing & Database Seeding

A script json_to_database.py was written to parse provided json initial data and inserted into local database.

The local database data was checked to be ok.

The initial database was seeded with provided initial data. (To transfer local database data, the local database was dumped to a .sql file. The file was then transfered to the remote server, and finally imported to the remote database.)

#### 2. API development

This week 3 APIs are assigned.

They are completed and logged to the API section above.

#### 3. AWS deployment

An AWS EC2 instance running ubuntu 24.04 was activated. It came preinstalled with python and git.

Files in the repository (develop branch) were downloaded to the instance by git clone & git pull.

Installed pip3, mySQL, FastAPI (including uvicorn), mysql-connector-python.

An elastic IP was associated with the EC2 instance.

The webapp was tested, then ran with nohup on.

Submitted the PR for review. (2024/05/29)