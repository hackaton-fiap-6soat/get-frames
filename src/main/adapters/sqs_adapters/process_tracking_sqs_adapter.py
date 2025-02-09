import boto3
import json
from main.ports.messaging_port import MessagingPort

class ProcessTrackingSQSAdapter(MessagingPort):
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
        return {
            "MessageBody": json.dumps({
                "id_usuario": message_attributes["id_usuario"],
                "processo": message_attributes["processo"],
                "nome_arquivo": message_attributes["nome_arquivo"],
                "status": message_attributes["status"]
            }),
        }