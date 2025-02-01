import boto3
from core.ports.messaging_port import MessagingPort

class SQSAdapter(MessagingPort):
    def __init__(self):
        self.client = boto3.client('sqs')

    def send_message(self, queue_url, message):
        sqs = boto3.client('sqs')
        try:
            sqs.send_message(QueueUrl=queue_url, **message)
            print("Mensagem enviada para o SQS com sucesso.")
        except Exception as e:
            raise Exception("Erro ao enviar mensagem para o SQS:", str(e))
    
    def build_message(message, type_message, user_uuid, file):
        return {
            "MessageBody": message,
            "MessageAttributes": {
                "Type": {
                    "StringValue": type_message,
                    "DataType": "String"
                },
                "User": {
                    "StringValue": user_uuid,
                    "DataType": "String"
                },
                "File": {
                    "StringValue": file,
                    "DataType": "String"
                }
            }
        }