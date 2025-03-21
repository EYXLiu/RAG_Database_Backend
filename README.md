# RAG Database Backend
Refer to [RAG_Database_Website](https://github.com/EYXLiu/RAG_Database_Website) for the NextJS Frontend

# About
* Currently not deployed as trying to reduce the docker image size for better Oracle Cloud Containerizing (currently 6gb o.O)
* Note, Oracle also believes it will take too much memory this is so sad 😔
* FastAPI endpoints to send requests to Supabase to grab the stored embeddings and texts
* Due to Supabase Limitations (rpc doesn't allow setof returns), a Redis Cache is created for faster data retrival
* Dockerized using docker-compile to run both redis and uvicorn endpoints, setup for images for Oracle Cloud deployment
* Used Oracle Cloud and SSH to upload files and run on an Oracle Cloud instance, containerized and deployed on an Oracle Cloud container
* Set up Cosine Similarity using an optimized numpy function to return the most relevant embeddings
* Created FastAPI endpoints to both set and get data from Supabase

# Docker deployment
* Run `docker-compile up --build` to create the docker images
* In the .env file, the Redis host should be 'redis-server' and the port should be '6379', which is declared in the docker-compose.yml file
* The API endpoint is now set to `0.0.0.0:8000`
* To stop, run `docker-compile down` to stop the images 
