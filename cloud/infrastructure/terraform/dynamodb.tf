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
