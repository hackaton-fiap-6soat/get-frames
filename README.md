# Sobre o Projeto
Uma simples função lambda capaz de extrair todos os frames de um determinado vídeo.

## Funcionamento
A Lambda é acionada a partir da **inserção** de vídeos `.mp4` em um Bucket de entrada. Após a extração de todos os frames do vídeo,
estes são compactados em um arquivo zip e armazenados em um Bucket de saída.

Em ambos os cenários de sucesso ou falha, uma mensagem SQS é enviada ao usuário, a fim de dar-lhe um feedback sobre a operação.
Em caso de sucesso, o usuário também receberá o link para que possa baixar o arquivo `zip`.

## Arquitetura
O projeto contempla o modelo de Arquitetura Hexagonal pelos seguintes motivos:
1. **Separação clara entre a lógica de negócio e a infraestrutura da aplicação**
2. **Flexibilidade**:
    - Atualmente, o projeto suporta apenas **FFMpeg** para a extração dos frames, **S3** para o armazenamento e
    **SQS** para o serviço de mensageria, porém, graças ao modelo de Ports and Adapters, é possível fazer com que
    ele seja compatível com outros serviços, como o Google Cloud Storage, por exemplo, o tornando mais abrangente
3. **Escalabilidade**:
    - Caso o projeto cresça o suficiente para ficar insustentável centralizado apenas em uma função lambda,
    está desacoplado o suficiente para que seja distribuído em microsserviços futuramente

## Limitações
Por ser um projeto bem simples, precisamos limitar a aplicação para aceitar vídeos de, no máximo, 10 segundos,
a fim de poupar o processamento, mantendo a qualidade e velocidade na entrega.