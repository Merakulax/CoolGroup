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
}

resource "aws_apigatewayv2_route" "sensor_ingest" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /sensor-data"
  target    = "integrations/${aws_apigatewayv2_integration.sensor_ingest.id}"
}

resource "aws_lambda_permission" "api_gw_ingest" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sensor_ingest.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*/sensor-data"
}
