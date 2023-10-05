terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.18"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.region
}

resource "aws_dynamodb_table" "movie_genre_table" {
  name           = "movielens_movie"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "movie_id"
  range_key      = "genre"

  attribute {
    name = "movie_id"
    type = "N"
  }

  attribute {
    name = "genre"
    type = "S"
  }

}