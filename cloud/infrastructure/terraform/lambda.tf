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
  publish          = true

  environment {
    variables = {
      DYNAMODB_TABLE           = aws_dynamodb_table.user_state.name
      HEALTH_TABLE             = aws_dynamodb_table.health_data.name
      ENV                      = var.environment
      PROJECT_NAME             = var.project_name
      STATE_REACTOR_FUNCTION_NAME = aws_lambda_function.state_reactor.function_name
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "sensor_ingest_concurrency" {
  function_name                     = aws_lambda_function.sensor_ingest.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.sensor_ingest.version
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
  publish          = true

  environment {
    variables = {
      DYNAMODB_TABLE           = aws_dynamodb_table.user_state.name
      HEALTH_TABLE             = aws_dynamodb_table.health_data.name
      USERS_TABLE              = aws_dynamodb_table.users.name
      ENV                      = var.environment
      PROACTIVE_COACH_FUNCTION = aws_lambda_function.proactive_coach.function_name
      STATE_REACTOR_FUNCTION   = aws_lambda_function.state_reactor.function_name
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "orchestrator_concurrency" {
  function_name                     = aws_lambda_function.orchestrator.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.orchestrator.version
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
  publish          = true

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.user_state.name
      ENV            = var.environment
      PROJECT_NAME   = var.project_name
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "demo_trigger_concurrency" {
  function_name                     = aws_lambda_function.demo_trigger.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.demo_trigger.version
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
  publish          = true

  environment {
    variables = {
      USERS_TABLE      = aws_dynamodb_table.users.name
      USER_STATE_TABLE = aws_dynamodb_table.user_state.name
      AVATAR_BUCKET    = aws_s3_bucket.avatars.id
      ENV              = var.environment
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "user_manager_concurrency" {
  function_name                     = aws_lambda_function.user_manager.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.user_manager.version
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
  timeout          = 300
  memory_size      = 3008
  layers           = [aws_lambda_layer_version.gcp_deps_layer.arn]
  publish          = true

  environment {
    variables = {
      USERS_TABLE      = aws_dynamodb_table.users.name
      HEALTH_TABLE     = aws_dynamodb_table.health_data.name
      USER_STATE_TABLE = aws_dynamodb_table.user_state.name
      AVATAR_CACHE_TABLE = aws_dynamodb_table.avatar_cache.name
      GCP_PROJECT_ID   = var.gcp_project_id
      GCP_REGION       = var.gcp_region
      GCP_API_KEY      = var.gcp_api_key
      AVATAR_BUCKET    = aws_s3_bucket.avatars.id
      GCS_BUCKET_NAME  = google_storage_bucket.video_assets.name
      ENV              = var.environment
      GOOGLE_CLOUD_PROJECT = var.gcp_project_id
      GOOGLE_CLOUD_LOCATION = var.gcp_region
      GOOGLE_GENAI_USE_VERTEXAI = "True"
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "avatar_generator_concurrency" {
  function_name                     = aws_lambda_function.avatar_generator.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.avatar_generator.version
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
  publish          = true
}

resource "aws_lambda_provisioned_concurrency_config" "echo_concurrency" {
  function_name                     = aws_lambda_function.echo.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.echo.version
}

# Zip the retriever function code
data "archive_file" "retriever_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/retriever"
  output_path = "${path.module}/.build/retriever.zip"
  excludes    = ["__pycache__"]
}

resource "aws_lambda_function" "context_retriever" {
  filename         = data.archive_file.retriever_zip.output_path
  function_name    = "${var.project_name}-context-retriever-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "context_retriever.handler"
  source_code_hash = data.archive_file.retriever_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 10
  memory_size      = 128
  publish          = true

  environment {
    variables = {
      HEALTH_TABLE = aws_dynamodb_table.health_data.name
      ENV          = var.environment
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "context_retriever_concurrency" {
  function_name                     = aws_lambda_function.context_retriever.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.context_retriever.version
}
