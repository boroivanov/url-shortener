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
