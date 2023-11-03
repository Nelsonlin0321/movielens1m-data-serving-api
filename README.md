# movielens1m-data-serving-api

## Run Recommender API Locally

```sh
python -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

source .env
uvicorn app.server:app --reload-dir app --host 0.0.0.0 --port 8000
```

## Build the docker

```sh
image_name=movielens1m-data-serving
docker build -t ${image_name}:latest -f ./Dockerfile . --platform linux/arm64/v8
docker run --env-file docker.env -p 5050:5050 -it --rm --name ${image_name} ${image_name}:latest
```

```sh
curl -X 'GET' \
  'http://0.0.0.0:8000/api/v1/movies/?page_size=12' \
  -H 'accept: application/json'
```

```sh
curl -X 'GET' \
  'http://0.0.0.0:8000/api/v1/movies/?genre=Animation&page_size=12' \
  -H 'accept: application/json'
```


```sh
image_name=movielens1m-data-serving-lambda
docker build -t ${image_name}:latest -f ./Dockerfile.aws.lambda  . --platform linux/arm64/v8
docker run --env-file docker.env -p 9000:8080 -it --rm --name ${image_name} ${image_name}:latest
```

```sh
# TEST healthcheck
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{
    "resource": "/api/health-check",
    "path": "/api/health-check",
    "httpMethod": "GET",
    "requestContext": {
    },
    "isBase64Encoded": false
}'
```

## Push To ECR
```sh
account_id=932682266260
region=ap-southeast-1
image_name=movielens1m-data-serving-lambda
repo_name=${image_name}
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account_id}.dkr.ecr.${region}.amazonaws.com
```


## Terraform Infra Deployment

```sh
terraform init
terraform fmt
terraform apply
```

```sh
terraform output -json > ./outputs.json
```

```sh
curl -X 'GET' \
  'https://jh9d4gng3e.execute-api.ap-southeast-1.amazonaws.com/prod/api/v1/movies/?genre=Animation&page_size=12' \
  -H 'accept: application/json'
```


```sh
curl -X 'GET' \
  'https://jh9d4gng3e.execute-api.ap-southeast-1.amazonaws.com/prod/api/v1/movies/search?q=black&limit=30' \
  -H 'accept: application/json'
```