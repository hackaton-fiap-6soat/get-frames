provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {}
}

data "aws_iam_role" "lab-role" {
  name = "LabRole"
}

variable s3_bucket {
  type = string
}

resource "aws_lambda_function" "application_entry" {
  function_name = "application_entry"
  handler       = "src/get_frames.py"
  runtime       = "python3.10"
  role          = data.aws_iam_role.lab-role.arn
  s3_bucket     = var.s3_bucket
  s3_key        = "get_frames.zip"

  environment {
    variables = {
      ENV_VAR = "value"
    }
  }

  tags = {
    Name = "get-frames-lambda"
  }
}

### General data sources
data "aws_vpc" "hackathon-vpc" {
  filter {
    name   = "tag:Name"
    values = ["hackathon-vpc"]
  }
}

resource "aws_security_group" "lambda_sg" {
  name        = "lambda_sg"
  description = "Security Group for Lambda function"
  vpc_id      = data.aws_vpc.hackathon-vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lambda-security-group"
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "ApplicationEntry"
}

# API Gateway Resource
resource "aws_api_gateway_resource" "hackathon-resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "frames"
}

# Nested Resource /frames/upload
resource "aws_api_gateway_resource" "upload_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.hackathon-resource.id # link it under /pedidos
  path_part   = "upload"
}

# Method GET on /frames/upload
resource "aws_api_gateway_method" "get_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.upload-resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration with Lambda for CPF
resource "aws_api_gateway_integration" "lambda_integration_video" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.upload_resource.id
  http_method             = aws_api_gateway_method.post_method_cpf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.application_entry.invoke_arn
  credentials             = data.aws_iam_role.lab-role.arn

  request_templates = {
    "application/json" = <<EOF
    {
      "body" : $input.json('$'),
      "linkVideo" : "$input.params('linkVideo')"
    }
    EOF
  }
}

# API Gateway Integration with Lambda (/frames/upload)
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.upload-resource.id
  http_method             = aws_api_gateway_method.get_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.application_entry.invoke_arn
  credentials             = data.aws_iam_role.lab-role.arn
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.application_entry.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/POST/frames/upload"
}

# Deploy API Gateway
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on   = [
    aws_api_gateway_integration.lambda_integration,
    aws_lambda_permission.api_gateway_permission,
    aws_api_gateway_integration.lambda_integration_video,    

    aws_lambda_permission.api_gateway_permission_register,
    aws_api_gateway_integration.lambda_integration_register
  ]
  rest_api_id  = aws_api_gateway_rest_api.api.id
  stage_name   = "prod"

  triggers = {
    redeployment = timestamp() # Força a atualização do deployment
  }

}