provider "aws" {
  region = "us-east-1"
}

# KMS key to encrypt/decrypt lambda env vars
resource "aws_kms_key" "url-shortener" {
  description = "Encrypt/Decrypt url-shortener lambda env vars"
}

resource "aws_kms_alias" "url-shortener" {
  name          = "alias/url-shortener"
  target_key_id = "${aws_kms_key.url-shortener.key_id}"
}

# DynamoDB table for lambda env vars
resource "aws_dynamodb_table" "url-shortener-envs" {
  name           = "url-shortener-envs"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "key"

  attribute {
    name = "key"
    type = "S"
  }
}

# DynamoDB table for short url tokens
resource "aws_dynamodb_table" "url-shortener-tokens" {
  name           = "url-shortener-tokens"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "token"

  attribute {
    name = "token"
    type = "S"
  }
}

# Lambda IAM Role
resource "aws_iam_role" "url-shortener-lambda-role" {
    name = "url-shortener-lambda-role"
    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# Lambda IAM Policy - CloudWatch Logs, DynamoDB, and KMS
resource "aws_iam_role_policy" "url-shortener-lambda-policy" {
    name = "url-shortener-lambda-policy"
    role = "${aws_iam_role.url-shortener-lambda-role.id}"
    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:DescribeKey",
        "kms:GetKeyPolicy"
      ],
      "Resource": [
        "arn:aws:kms:*:*:alias/url-shortener"
      ],
      "Effect": "Allow"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:*"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/url-shortener*"
    }
  ]
}
EOF
}
