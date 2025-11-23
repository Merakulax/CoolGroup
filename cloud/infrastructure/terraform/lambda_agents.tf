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
  publish          = true

  environment {
    variables = {
      USERS_TABLE      = aws_dynamodb_table.users.name
      HEALTH_TABLE     = aws_dynamodb_table.health_data.name
      DYNAMODB_TABLE   = aws_dynamodb_table.user_state.name # User State
      MODEL_ID         = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
      ENV              = var.environment
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "proactive_coach_concurrency" {
  function_name                     = aws_lambda_function.proactive_coach.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.proactive_coach.version
}

# --- STATE REACTOR SYSTEM ---

# Archive for the whole State Reactor package (includes Orchestrator + Experts + Supervisor)
data "archive_file" "state_reactor_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda/agents/state_reactor"
  output_path = "${path.module}/.build/state_reactor.zip"
  excludes    = ["__pycache__"]
}

# 1. State Reactor Orchestrator
resource "aws_lambda_function" "state_reactor" {
  filename         = data.archive_file.state_reactor_zip.output_path
  function_name    = "${var.project_name}-state-reactor-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.state_reactor_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  publish          = true

  environment {
    variables = {
      USERS_TABLE            = aws_dynamodb_table.users.name
      HEALTH_TABLE           = aws_dynamodb_table.health_data.name
      DYNAMODB_TABLE         = aws_dynamodb_table.user_state.name
      CONTEXT_RETRIEVER_LAMBDA_ARN = aws_lambda_function.context_retriever.arn
      ENV                    = var.environment
      # Child Functions
      ACTIVITY_FUNCTION      = aws_lambda_function.expert_activity.function_name
      VITALS_FUNCTION        = aws_lambda_function.expert_vitals.function_name
      WELLBEING_FUNCTION     = aws_lambda_function.expert_wellbeing.function_name
      SUPERVISOR_FUNCTION    = aws_lambda_function.expert_supervisor.function_name
      CHARACTERIZER_FUNCTION = aws_lambda_function.characterizer.function_name
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "state_reactor_concurrency" {
  function_name                     = aws_lambda_function.state_reactor.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.state_reactor.version
}

# 2. Expert: Activity
resource "aws_lambda_function" "expert_activity" {
  filename         = data.archive_file.state_reactor_zip.output_path
  function_name    = "${var.project_name}-expert-activity-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "experts.activity.handler"
  source_code_hash = data.archive_file.state_reactor_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256
  publish          = true

  environment {
    variables = {
      MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "expert_activity_concurrency" {
  function_name                     = aws_lambda_function.expert_activity.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.expert_activity.version
}

# 3. Expert: Vitals
resource "aws_lambda_function" "expert_vitals" {
  filename         = data.archive_file.state_reactor_zip.output_path
  function_name    = "${var.project_name}-expert-vitals-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "experts.vitals.handler"
  source_code_hash = data.archive_file.state_reactor_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256
  publish          = true

  environment {
    variables = {
      MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "expert_vitals_concurrency" {
  function_name                     = aws_lambda_function.expert_vitals.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.expert_vitals.version
}

# 4. Expert: Wellbeing
resource "aws_lambda_function" "expert_wellbeing" {
  filename         = data.archive_file.state_reactor_zip.output_path
  function_name    = "${var.project_name}-expert-wellbeing-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "experts.wellbeing.handler"
  source_code_hash = data.archive_file.state_reactor_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256
  publish          = true

  environment {
    variables = {
      MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "expert_wellbeing_concurrency" {
  function_name                     = aws_lambda_function.expert_wellbeing.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.expert_wellbeing.version
}

# 5. Supervisor
resource "aws_lambda_function" "expert_supervisor" {
  filename         = data.archive_file.state_reactor_zip.output_path
  function_name    = "${var.project_name}-supervisor-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "supervisor.handler"
  source_code_hash = data.archive_file.state_reactor_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256
  publish          = true

  environment {
    variables = {
      MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "expert_supervisor_concurrency" {
  function_name                     = aws_lambda_function.expert_supervisor.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.expert_supervisor.version
}

# 6. Characterizer
resource "aws_lambda_function" "characterizer" {
  filename         = data.archive_file.state_reactor_zip.output_path
  function_name    = "${var.project_name}-characterizer-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "characterizer.handler"
  source_code_hash = data.archive_file.state_reactor_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256
  publish          = true

  environment {
    variables = {
      MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
    }
  }
}

resource "aws_lambda_provisioned_concurrency_config" "characterizer_concurrency" {
  function_name                     = aws_lambda_function.characterizer.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.characterizer.version
}