#!/bin/sh

set -e
ROOT=$(dirname $0)
cd "$ROOT"

sudo rm -Rf ./endpoints/apis ./endpoints/models ./endpoints/router_init.py
mkdir -p "$ROOT/endpoints"

sudo rm -Rf ./openapi-generator-output
docker run --rm -v "${PWD}":/app openapitools/openapi-generator-cli:latest-release generate  \
    -i /app/spec.yml  -g python-fastapi   -o /app/openapi-generator-output \
    --additional-properties=packageName=endpoints --additional-properties=fastapiImplementationPackage=endpoints

sudo chown "$USER":"$USER" -R openapi-generator-output
rm -Rf endpoints/apis endpoints/models
mv openapi-generator-output/src/endpoints/apis endpoints/
mv openapi-generator-output/src/endpoints/models endpoints/
mv openapi-generator-output/src/endpoints/main.py endpoints/router_init.py
rm -Rf openapi-generator-output