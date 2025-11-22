

# --- AGENT: Proactive Coach ---
data "archive_file" "proactive_coach_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/agents/proactive_coach"
  output_path = "${path.module}/.build/proactive_coach.zip"
  excludes    = ["__pycache__"]
}

resource "aws_lambda_function" "proactive_coach" {
  filename         = data.archive_file.proactive_coach_zip.output_path
  function_name    = "${var.project_name}-proactive-coach-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.proactive_coach_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      USERS_TABLE      = aws_dynamodb_table.users.name
      HEALTH_TABLE     = aws_dynamodb_table.health_data.name
      DYNAMODB_TABLE   = aws_dynamodb_table.user_state.name # User State
      MODEL_ID         = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
      ENV              = var.environment
    }
  }
}

# --- AGENT: State Reactor ---
data "archive_file" "state_reactor_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/agents/state_reactor"
  output_path = "${path.module}/.build/state_reactor.zip"
  excludes    = ["__pycache__"]
}

resource "aws_lambda_function" "state_reactor" {
  filename         = data.archive_file.state_reactor_zip.output_path
  function_name    = "${var.project_name}-state-reactor-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.state_reactor_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      USERS_TABLE            = aws_dynamodb_table.users.name
      HEALTH_TABLE           = aws_dynamodb_table.health_data.name
      DYNAMODB_TABLE         = aws_dynamodb_table.user_state.name
      MODEL_ID               = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
      CONTEXT_RETRIEVER_LAMBDA_ARN = aws_lambda_function.context_retriever.arn
      ENV                    = var.environment
    }
  }
}
