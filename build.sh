#!/bin/bash

docker build -t rag_server .

docker run -d -p 8080:8080 --name rag_server_container rag_server
