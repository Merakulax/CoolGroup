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
      USERS_TABLE    = aws_dynamodb_table.users.name
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

# Zip the user manager function code
data "archive_file" "user_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/user"
  output_path = "${path.module}/.build/user.zip"
  excludes    = ["__pycache__"]
}

resource "aws_lambda_function" "user_manager" {
  filename         = data.archive_file.user_zip.output_path
  function_name    = "${var.project_name}-user-manager-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "manager.handler"
  source_code_hash = data.archive_file.user_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      USERS_TABLE      = aws_dynamodb_table.users.name
      USER_STATE_TABLE = aws_dynamodb_table.user_state.name
      AVATAR_BUCKET    = aws_s3_bucket.avatars.id
      ENV              = var.environment
    }
  }
}

# Zip the avatar generator function code
data "archive_file" "avatar_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/avatar"
  output_path = "${path.module}/.build/avatar.zip"
  excludes    = ["__pycache__"]
}

resource "aws_lambda_function" "avatar_generator" {
  filename         = data.archive_file.avatar_zip.output_path
  function_name    = "${var.project_name}-avatar-generator-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "generator.handler"
  source_code_hash = data.archive_file.avatar_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 3008
  layers           = [aws_lambda_layer_version.gcp_deps_layer.arn]

  environment {
    variables = {
      USERS_TABLE      = aws_dynamodb_table.users.name
      HEALTH_TABLE     = aws_dynamodb_table.health_data.name
      USER_STATE_TABLE = aws_dynamodb_table.user_state.name
      GCP_PROJECT_ID   = var.gcp_project_id
      GCP_REGION       = var.gcp_region
      GCP_API_KEY      = var.gcp_api_key
      AVATAR_BUCKET    = aws_s3_bucket.avatars.id
      ENV              = var.environment
      GOOGLE_CLOUD_PROJECT = var.gcp_project_id
      GOOGLE_CLOUD_LOCATION = var.gcp_region
      GOOGLE_GENAI_USE_VERTEXAI = "True"
    }
  }
}

# Zip the echo function code
data "archive_file" "echo_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/echo"
  output_path = "${path.module}/.build/echo.zip"
  excludes    = ["__pycache__"]
}

resource "aws_lambda_function" "echo" {
  filename         = data.archive_file.echo_zip.output_path
  function_name    = "${var.project_name}-echo-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "echo.handler"
  source_code_hash = data.archive_file.echo_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 5
  memory_size      = 128
}
