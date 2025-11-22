resource "aws_cloudwatch_event_rule" "coach_schedule" {
  name                = "${var.project_name}-coach-schedule-${var.environment}"
  description         = "Triggers the Proactive Health Coach every hour"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "trigger_orchestrator" {
  rule      = aws_cloudwatch_event_rule.coach_schedule.name
  target_id = "OrchestratorLambda"
  arn       = aws_lambda_function.orchestrator.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.orchestrator.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.coach_schedule.arn
}
