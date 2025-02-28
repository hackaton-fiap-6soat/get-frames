terraform {
  backend "s3" {
    bucket = "hackathon-6soat-processed-videos-bucket"
    key    = "lambda.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"  # Ajuste conforme necessário
}

# Variáveis para os buckets S3 preexistentes

variable "tf_state_bucket" {
  type = string
  description = "Bucket S3 de artefatos para a Lambda"
}

variable "input_s3_bucket" {
  type = string
  description = "Bucket S3 de entrada que aciona a Lambda"
}

variable "output_s3_bucket" {
  type = string
  description = "Bucket S3 de saída para armazenar os resultados"
}

variable "user_sqs" {
  type = string
  description = "SQS para envio de mensagens"
}

variable "process_tracking_sqs_url" {
  type = string
  description = "SQS para envio de mensagens"
}

data "aws_vpc" "hackathon-vpc" {
  filter {
    name   = "tag:Name"
    values = ["fiap-hackathon-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  filter {
    name = "vpc-id"
    values = [data.aws_vpc.hackathon-vpc.id]
  }

  filter {
    name = "tag:Name"
    values = ["*private*"]
  }
}

resource "aws_s3_bucket" "output_s3_bucket" {
  bucket = var.output_s3_bucket
  force_destroy = true
}


resource "aws_security_group" "lambda" {
  name        = "lambda_sg"
  description = "Security group for Lambda"
  vpc_id      = data.aws_vpc.hackathon-vpc.id

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Package the Lambda function
data "archive_file" "process_s3_files" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/../video_processor.zip"
}

resource "aws_lambda_layer_version" "ffmpeg_layer" {
  s3_bucket           = var.tf_state_bucket
  s3_key              = "ffmpeg-layer.zip"
  layer_name          = "ffmpeg"
  compatible_runtimes = ["python3.10"]
}

resource "aws_lambda_function" "process_s3_files" {
  filename         = "${path.module}/../video_processor.zip"
  function_name    = "process_s3_files"
  handler          = "main.entry_point.lambda_handler.lambda_handler"
  runtime          = "python3.10"
  source_code_hash = data.archive_file.process_s3_files.output_base64sha256
  timeout          = 900
  role             = data.aws_iam_role.lab_role.arn
  memory_size      = 2048

  layers = [aws_lambda_layer_version.ffmpeg_layer.arn]

  environment {
    variables = {
      INPUT_BUCKET  = var.input_s3_bucket
      OUTPUT_BUCKET = aws_s3_bucket.output_s3_bucket.bucket
      FFMPEG_PATH   = "/opt/bin/ffmpeg"
      USER_SQS_URL  = var.user_sqs
      PROCESS_TRACKING_SQS_URL = var.process_tracking_sqs_url
    }
  }

  vpc_config {
    subnet_ids = data.aws_subnets.private_subnets.ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  tags = {
    Name        = "LambdaProcess"
    Environment = "Dev"
  }

  depends_on = [ data.archive_file.process_s3_files ]

  ephemeral_storage {
    size = 2048 # Min 512 MB and the Max 10240 MB
  }
}

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

  depends_on = [
    aws_lambda_function.process_s3_files,  # Garante que a Lambda já foi criada
    aws_lambda_permission.allow_s3
  ]
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