output "api_endpoint" {
  description = "HTTP API Endpoint URL"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "dynamodb_table_name" {
  description = "Name of the User State DynamoDB table"
  value       = aws_dynamodb_table.user_state.name
}
