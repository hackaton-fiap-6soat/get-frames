provider "aws" {
  region = "us-east-1"  # Ajuste para a região desejada
}

# Criar bucket S3
# resource "aws_s3_bucket" "s3_bucket" {
#   bucket = "meu-bucket-de-arquivos"  # Nome único global

#   tags = {
#     Name        = "InputBucket"
#     Environment = "Dev"
#   }
# }

variable s3_bucket {
  type = string
}

# Criar função Lambda
resource "aws_lambda_function" "process_s3_files" {
  function_name    = "process_s3_files_lambda"
  handler          = "src/get_frames.py"
  runtime          = "python3.10"  # Ajuste para o runtime necessário
  role             = data.aws_iam_role.lab_role.arn
  timeout          = 30
  memory_size      = 256

  # # Carrega código a partir de um arquivo ZIP
  # filename         = "lambda_function.zip"
  # source_code_hash = filebase64sha256("lambda_function.zip")

  environment {
    variables = {
      BUCKET_NAME = var.s3_bucket
    }
  }
}

# Data source para obter a role LabRole do AWS Academy
data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

# Permissão para que o S3 invoque a Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_s3_files.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.s3_bucket.arn
}

# Configurar evento no bucket para chamar a Lambda quando novos arquivos forem criados
resource "aws_s3_bucket_notification" "s3_event_trigger" {
  bucket = var.s3_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_s3_files.arn
    events              = ["s3:ObjectCreated:*"]  # Invoca a Lambda ao adicionar arquivos
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

# Output para mostrar o bucket criado
output "s3_bucket_name" {
  value = var.s3_bucket
}

output "lambda_function_name" {
  value = aws_lambda_function.process_s3_files.function_name
}