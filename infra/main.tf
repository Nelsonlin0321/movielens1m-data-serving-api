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
  write_capacity = 1
  hash_key       = "genre"
  range_key      = "movie_id"

  attribute {
    name = "movie_id"
    type = "N"
  }

  attribute {
    name = "genre"
    type = "S"
  }

  attribute {
    name = "rank"
    type = "N"
  }

  global_secondary_index {
    name               = "rank_index"
    hash_key           = "rank"
    range_key          = "movie_id"
    write_capacity     = 1
    read_capacity      = 5
    projection_type    = "ALL"
  }

}