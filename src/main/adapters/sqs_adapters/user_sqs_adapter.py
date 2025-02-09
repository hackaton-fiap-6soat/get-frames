import boto3
import json
from main.ports.messaging_port import MessagingPort

class UserSQSAdapter(MessagingPort):
    def __init__(self):
        self.client = boto3.client('sqs')

    def send_message(self, queue_url, message):
        sqs = boto3.client('sqs')
        try:
            sqs.send_message(QueueUrl=queue_url, **message)
            print("Mensagem enviada para o SQS com sucesso.")
        except Exception as e:
            raise Exception("Erro ao enviar mensagem para o SQS:", str(e))
    
    def build_message(self, message_attributes):
        link_arquivo = message_attributes["link_arquivo"] if hasattr(message_attributes, "link_arquivo") else None
        return {
            "MessageBody": json.dumps({
                "id_usuario": message_attributes["id_usuario"],
                "link_arquivo": link_arquivo
            }),
        }