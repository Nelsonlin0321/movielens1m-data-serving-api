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
  read_capacity  = 10
  write_capacity = 10
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

  attribute {
    name = "release_year"
    type = "N"
  }

  attribute {
    name = "rating"
    type = "N"
  }

  global_secondary_index {
    name               = "rank-release-year-index"
    hash_key           = "rank"
    range_key          = "release_year"
    write_capacity     = 1
    read_capacity      = 1
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "genre-release-year-index"
    hash_key           = "genre"
    range_key          = "release_year"
    write_capacity     = 1
    read_capacity      = 1
    projection_type    = "ALL"
  }


  global_secondary_index {
    name               = "rank-rating-index"
    hash_key           = "rank"
    range_key          = "rating"
    write_capacity     = 1
    read_capacity      = 1
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "genre-rating-index"
    hash_key           = "genre"
    range_key          = "rating"
    write_capacity     = 1
    read_capacity      = 1
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "movie-id-rank-index"
    hash_key           = "movie_id"
    range_key          = "rank"
    write_capacity     = 1
    read_capacity      = 1
    projection_type    = "ALL"
  }

}



data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "${var.lambda_function_name}-iam-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14
}

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [aws_cloudwatch_log_group.lambda_log_group.arn]
  }
}

resource "aws_iam_policy" "lambda_logging_policy" {
  name        = "${var.lambda_function_name}_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging_policy.arn
}


data "aws_iam_policy_document" "lambda_dynamodb_access" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query",
    ]

    resources = ["${aws_dynamodb_table.movie_genre_table.arn}/*",
    aws_dynamodb_table.movie_genre_table.arn]
  }
}

resource "aws_iam_policy" "lambda_dynamodb_access" {
  name        = "movielens_lambda_role"
  path        = "/"
  description = "IAM policy of dynamodb access for lambda "
  policy      = data.aws_iam_policy_document.lambda_dynamodb_access.json
}


resource "aws_iam_role_policy_attachment" "lambda_dynamodb_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_dynamodb_access.arn
}



resource "aws_lambda_function" "movielens1m-data-serving-lambda" {
  function_name = var.lambda_function_name

  timeout       = 5 # seconds
  image_uri     = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.repository_name}:latest"
  package_type  = "Image"
  architectures = ["x86_64"]
  depends_on = [
    aws_cloudwatch_log_group.lambda_log_group,
    aws_iam_role_policy_attachment.lambda_logs_policy_attachment,
    aws_iam_role_policy_attachment.lambda_dynamodb_policy_attachment
  ]
  role = aws_iam_role.iam_for_lambda.arn
}


resource "aws_api_gateway_rest_api" "lambda_rest_gateway" {
  name = "${var.lambda_function_name}-api"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.lambda_rest_gateway.id}"
  parent_id   = "${aws_api_gateway_rest_api.lambda_rest_gateway.root_resource_id}"
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = "${aws_api_gateway_rest_api.lambda_rest_gateway.id}"
  resource_id   = "${aws_api_gateway_resource.proxy.id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = "${aws_api_gateway_rest_api.lambda_rest_gateway.id}"
  resource_id = "${aws_api_gateway_method.proxy.resource_id}"
  http_method = "${aws_api_gateway_method.proxy.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.movielens1m-data-serving-lambda.invoke_arn}"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.lambda_rest_gateway.execution_arn}/*/*"
}


resource "aws_api_gateway_deployment" "lambda_rest_prod_gateway" {
  depends_on = [
    aws_api_gateway_integration.lambda,
  ]

  rest_api_id = "${aws_api_gateway_rest_api.lambda_rest_gateway.id}"
  stage_name  = "prod"
}
