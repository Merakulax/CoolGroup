# Zip the ingest function code (This assumes the code exists locally)
data "archive_file" "ingest_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/ingest"
  output_path = "${path.module}/.build/ingest.zip"
  excludes    = ["requirements.txt", "__pycache__"]
}

resource "aws_lambda_function" "sensor_ingest" {
  filename         = data.archive_file.ingest_zip.output_path
  function_name    = "${var.project_name}-sensor-ingest-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "sensor_ingest.handler"
  source_code_hash = data.archive_file.ingest_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.user_state.name
      HEALTH_TABLE   = aws_dynamodb_table.health_data.name
      ENV            = var.environment
      PROJECT_NAME   = var.project_name
    }
  }
}

# Zip the orchestrator function code
data "archive_file" "orchestrator_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/orchestrator"
  output_path = "${path.module}/.build/orchestrator.zip"
  excludes    = ["requirements.txt", "__pycache__"]
}

resource "aws_lambda_function" "orchestrator" {
  filename         = data.archive_file.orchestrator_zip.output_path
  function_name    = "${var.project_name}-orchestrator-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "agentic_loop.handler" # Assuming handler name
  source_code_hash = data.archive_file.orchestrator_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 60 # Bedrock calls can be slow
  memory_size      = 256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.user_state.name
      HEALTH_TABLE   = aws_dynamodb_table.health_data.name
      ENV            = var.environment
    }
  }
}

# Zip the demo trigger function code
data "archive_file" "demo_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/demo"
  output_path = "${path.module}/.build/demo.zip"
  excludes    = ["__pycache__"]
}

resource "aws_lambda_function" "demo_trigger" {
  filename         = data.archive_file.demo_zip.output_path
  function_name    = "${var.project_name}-demo-trigger-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "trigger.handler"
  source_code_hash = data.archive_file.demo_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.user_state.name
      ENV            = var.environment
      PROJECT_NAME   = var.project_name
    }
  }
}
