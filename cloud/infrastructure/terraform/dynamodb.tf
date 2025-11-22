resource "aws_dynamodb_table" "user_state" {
  name           = "${var.project_name}-user-state-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  # GSI for querying by pet state if needed later, keeping it simple for now

  tags = {
    Name = "${var.project_name}-user-state"
  }
}

resource "aws_dynamodb_table" "health_data" {
  name           = "${var.project_name}-health-data-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  range_key      = "timestamp"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Name = "${var.project_name}-health-data"
  }
}

resource "aws_dynamodb_table" "users" {
  name           = "${var.project_name}-users-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-users"
  }
}
