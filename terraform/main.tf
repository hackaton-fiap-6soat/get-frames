provider "aws" {
  region = "us-east-1"  # Ajuste conforme necessário
}

# Variáveis para os buckets S3 preexistentes
variable "input_s3_bucket" {
  type = string
  description = "Bucket S3 de entrada que aciona a Lambda"
}

variable "output_s3_bucket" {
  type = string
  description = "Bucket S3 de saída para armazenar os resultados"
}

# Criar função Lambda usando o bucket de saída para armazenar o código

# Package the Lambda function
data "archive_file" "process_s3_files" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/get_frames.zip"
}

resource "aws_lambda_function" "process_s3_files" {
  filename         = "${path.module}/get_frames.zip"
  function_name    = "process_s3_files"
  # role             = data.aws_iam_role.LabRole.arn
  handler          = "src/get_frames.lambda_handler"
  runtime          = "python3.10"
  source_code_hash = data.archive_file.process_s3_files.output_base64sha256
  timeout          = 10
  role             = data.aws_iam_role.lab_role.arn
  memory_size      = 256
  # s3_bucket        = var.output_s3_bucket
  # s3_key           = "get_frames.zip"

  environment {
    variables = {
      INPUT_BUCKET  = var.input_s3_bucket
      OUTPUT_BUCKET = var.output_s3_bucket
    }
  }

  tags = {
    Name        = "LambdaProcess"
    Environment = "Dev"
  }

  depends_on = [ data.archive_file.process_s3_files ]
}
# resource "aws_lambda_function" "process_s3_files" {
#   function_name    = "process_s3_files_lambda"
#   handler          = "src/get_frames.lambda_handler"
#   runtime          = "python3.10"
#   role             = data.aws_iam_role.lab_role.arn
#   timeout          = 30
#   memory_size      = 256
#   s3_bucket        = var.output_s3_bucket
#   s3_key           = "get_frames.zip"

#   environment {
#     variables = {
#       INPUT_BUCKET  = var.input_s3_bucket
#       OUTPUT_BUCKET = var.output_s3_bucket
#     }
#   }

#   tags = {
#     Name        = "LambdaProcess"
#     Environment = "Dev"
#   }
# }

# Data source para obter a role LabRole do AWS Academy
data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

# Permissão para que o bucket de entrada invoque a Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_s3_files.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.input_s3_bucket}"
}

# Configurar evento no bucket de entrada para acionar a Lambda
resource "aws_s3_bucket_notification" "s3_event_trigger" {
  bucket = var.input_s3_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_s3_files.arn
    events              = ["s3:ObjectCreated:*"]  # Invoca a Lambda ao adicionar arquivos
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

# Outputs para verificar os recursos criados/configurados
output "lambda_function_name" {
  value = aws_lambda_function.process_s3_files.function_name
}

output "input_s3_bucket" {
  value = var.input_s3_bucket
}

output "output_s3_bucket" {
  value = var.output_s3_bucket
}