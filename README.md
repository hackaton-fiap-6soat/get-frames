# Sobre o Projeto
Uma simples função lambda capaz de extrair todos os frames de um determinado vídeo.

# Funcionamento
A Lambda é acionada a partir da **inserção** de vídeos `.mp4` em um Bucket de entrada. Após a extração de todos os frames do vídeo,
estes são compactados em um arquivo zip e armazenados em um Bucket de saída.

Em ambos os cenários de sucesso ou falha, uma mensagem SQS é enviada ao usuário, a fim de dar-lhe um feedback sobre a operação.
Em caso de sucesso, o usuário também receberá o link para que possa baixar o arquivo `zip`.

# Arquitetura
O projeto contempla o modelo de Arquitetura Hexagonal pelos seguintes motivos:
1. **Separação clara entre a lógica de negócio e a infraestrutura da aplicação**
2. **Flexibilidade**:
    - Atualmente, o projeto suporta apenas **FFMpeg** para a extração dos frames, **S3** para o armazenamento e
    **SQS** para o serviço de mensageria, porém, graças ao modelo de Ports and Adapters, é possível fazer com que
    ele seja compatível com outros serviços, como o Google Cloud Storage, por exemplo, o tornando mais abrangente
3. **Escalabilidade**:
    - Caso o projeto cresça o suficiente para ficar insustentável centralizado apenas em uma função lambda,
    está desacoplado o suficiente para que seja distribuído em microsserviços futuramente

# Limitações
Por ser um projeto bem simples, precisamos limitar a aplicação para aceitar vídeos de, no máximo, 10 segundos,
a fim de poupar o processamento, mantendo a qualidade e velocidade na entrega.

# Setup
## Pré Requisitos
- AWS Cli
- Python

## Preparando o Ambiente (local)
(você pode pular e seguir a próxima seção para rodar com `github actions`)
1. Clone o projeto:
    ```sh
    git clone git@github.com:hackaton-fiap-6soat/get-frames.git
    ```

2. Configure as seguintes variáveis de ambiente:

    2.1. `AWS_ACCESS_KEY_ID`

    2.2. `AWS_SECRET_ACCESS_KEY`

    2.3. `AWS_SESSION_TOKEN`

    2.4. `OUTPUT_BUCKET` (bucket de saída, onde serão armazenados os frames zipados)

    2.5. `INPUT_BUCKET` (bucket de entrada, onde os vídeos serão armazenados antes do processamento)

    2.6. `SQS_URL` (URL do serviço SQS)

    2.7. `AWS_DEFAULT_REGION`

3. Suba o projeto com o terraform:

    3.1. Init:
    ```bash
    terraform init -backend-config="bucket=${OUTPUT_BUCKET}" -backend-config="key=lambda.tfstate" -backend-config="region=us-east-1"
    ```

    3.2. Plan:
    ```bash
    terraform plan -out=tfplan -var "output_s3_bucket=${OUTPUT_BUCKET}" -var "input_s3_bucket=${INPUT_BUCKET}" -var "sqs=${SQS_URL}"
    ```

    3.3. Apply:
    ```bash
    terraform apply -auto-approve -var "output_s3_bucket=${OUTPUT_BUCKET}" -var "input_s3_bucket=${INPUT_BUCKET}" -var "sqs=${SQS_URL}"
    ```

## Testando com Github Actions
Após configurar as variáveis de ambientes informadas na seção anterior, rodar os jobs com o `github actions`.

As actions são ativadas sempre que há um push na main (via PR)