resource "aws_lambda_layer_version" "gcp_deps_layer" {
  layer_name          = "${var.project_name}-gcp-deps-layer-${var.environment}"
  compatible_runtimes = ["python3.11"]

  filename        = data.archive_file.gcp_deps_layer_zip.output_path
  source_code_hash = data.archive_file.gcp_deps_layer_zip.output_base64sha256
}

data "archive_file" "gcp_deps_layer_zip" {
  type        = "zip"
  source_dir  = "../../../lambda_layers/gcp_deps"
  output_path = "${path.module}/.build/gcp_deps_layer.zip"
}
