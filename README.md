# RAG Database Backend
Refer to [RAG_Database_Website](https://github.com/EYXLiu/RAG_Database_Website) for the NextJS Frontend

# About
* Likely not currently deployed as cloud services do not offer the capacity to run sentence_embeddings on a free account 😔
* FastAPI endpoints to send requests to Supabase to grab the stored embeddings and texts
* Due to Supabase Limitations (rpc doesn't allow setof returns), a Redis Cache is created for faster data retrival
* Dockerized using docker-compile to run both redis and uvicorn endpoints, setup for images for Oracle Cloud deployment
* Oracle Cloud deployment work in progress as the image size is ~6gb and trying to optimize it
* Set up Cosine Similarity using an optimized numpy function to return the most relevant embeddings
* Created FastAPI endpoints to both set and get data from Supabase

# Docker deployment
* Run `docker-compile up --build` to create the docker images
* In the .env file, the Redis host should be 'redis-server' and the port should be '6379', which is declared in the docker-compose.yml file
* The API endpoint is now set to `0.0.0.0:8000`
* To stop, run `docker-compile down` to stop the images 
