resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# Integration for Sensor Ingest
resource "aws_apigatewayv2_integration" "sensor_ingest" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.sensor_ingest.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "sensor_ingest" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /api/v1/user/{user_id}/data"
  target    = "integrations/${aws_apigatewayv2_integration.sensor_ingest.id}"
}

resource "aws_lambda_permission" "api_gw_ingest" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sensor_ingest.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*/api/v1/user/*/data"
}

# Integration for Demo Trigger
resource "aws_apigatewayv2_integration" "demo_trigger" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.demo_trigger.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "demo_trigger" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /api/v1/demo/trigger"
  target    = "integrations/${aws_apigatewayv2_integration.demo_trigger.id}"
}

resource "aws_lambda_permission" "api_gw_demo" {
  statement_id  = "AllowExecutionFromAPIGatewayDemo"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.demo_trigger.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*/api/v1/demo/trigger"
}

# Integration for User Manager
resource "aws_apigatewayv2_integration" "user_manager" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.user_manager.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "create_user" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /api/v1/users"
  target    = "integrations/${aws_apigatewayv2_integration.user_manager.id}"
}

resource "aws_apigatewayv2_route" "get_user" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /api/v1/users/{user_id}"
  target    = "integrations/${aws_apigatewayv2_integration.user_manager.id}"
}

resource "aws_apigatewayv2_route" "get_upload_url" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /api/v1/users/{user_id}/avatar/upload-url"
  target    = "integrations/${aws_apigatewayv2_integration.user_manager.id}"
}

resource "aws_lambda_permission" "api_gw_user" {
  statement_id  = "AllowExecutionFromAPIGatewayUser"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.user_manager.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*/api/v1/users*"
}

# ... (removed duplicate api_gw_user_avatar_state)

# Integration for Avatar Generator
resource "aws_apigatewayv2_integration" "avatar_generator" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.avatar_generator.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_avatar_state" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /api/v1/user/{user_id}/state"
  target    = "integrations/${aws_apigatewayv2_integration.user_manager.id}"
}

resource "aws_lambda_permission" "api_gw_user_avatar_state" {
  statement_id  = "AllowExecutionFromAPIGatewayUserAvatarState"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.user_manager.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*/api/v1/user/*/state"
}

resource "aws_lambda_permission" "api_gw_avatar" {
  statement_id  = "AllowExecutionFromAPIGatewayAvatar"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.avatar_generator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*/avatar/*"
}

# Integration for Echo
resource "aws_apigatewayv2_integration" "echo" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.echo.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "echo" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /api/v1/echo"
  target    = "integrations/${aws_apigatewayv2_integration.echo.id}"
}

resource "aws_lambda_permission" "api_gw_echo" {
  statement_id  = "AllowExecutionFromAPIGatewayEcho"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.echo.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*/api/v1/echo"
}
