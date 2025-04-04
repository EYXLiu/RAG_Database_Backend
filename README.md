# RAG Database Backend
Tech Stack: Python, FastAPI, Supabase, Redis, docker, docker-compile, Postman, JWT, Oracle Cloud, Numpy, Pandas, HuggingFace Transformers

# About
* Currently not deployed as trying to reduce the docker image size for better Oracle Cloud Containerizing (currently 6gb o.O)
* Note, Oracle also believes it will take too much memory this is so sad 😔, and does not allow docker to compile the images
* FastAPI endpoints to send requests to both Supabase and the Custom Database to grab the stored embeddings and texts
* Due to Supabase Limitations (rpc doesn't allow setof returns), a Redis Cache is created for faster data retrival
* Dockerized using docker-compile to run both redis and uvicorn endpoints, setup for images for Oracle Cloud deployment
* Used Oracle Cloud and SSH to upload files and run on an Oracle Cloud instance, containerized and deployed on an Oracle Cloud container
* Set up Cosine Similarity using an optimized numpy function to return the most relevant embeddings
* Created a custom JSON and TXT database in replacement for Supabase, more details below
* Created custom Authentication API endpoints using JWT for secure data transfer, more details below
* API Endpoints tested in both NextJS/Web fetch as well as Postman for testing

# Custom Database Storage
* Created a custom BTree database class for a sorted database, allowing for local data management, as used in PostgreSQL
* Database class includes the BTree, a dictionary for unordered storing of TXT file locations, a JSON file to store the unordered dictionary, and a TXT file to store the actual data
* Wrote custom CRUD operations for Get, Post, Update, and Delete functions and API endpoints for the database
* GET also includes current SQL functions like filtering, sorting, and getting top X rows, following SQL order of operations and using regex for pattern matching in queries
* Adapted FastAPI endpoints to use the custom database
* Still using Redis Caching as reading from the TXT file is much slower due to I/O operations

# Custom Secure Authentication
* Created custom Authentication classes on both frontend and backend for login
* Used same database as above for storage, updating whenever called and on logout
* Uses JWT for secure data transfer, as well as JWT timeouts for security reasons
* Uses Redis caching for logout/blacklisted tokens also for security reasons, including a timeout to save memory for invalid tokens

# Docker deployment
* Run `docker-compile up --build` to create the docker images - make sure you have `docker v2.32.4`
* In the .env file, the Redis host should be 'redis-server' and the port should be '6379', which is declared in the docker-compose.yml file
* The API endpoint is now set to `0.0.0.0:8000`
* To stop, run `docker-compile down` to stop the images 

#### Refer to [RAG_Database_Website](https://github.com/EYXLiu/RAG_Database_Website) for the NextJS Frontend 
