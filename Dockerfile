# Usa uma imagem oficial do Python, versão leve (slim)
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para algumas bibliotecas Python
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Adiciona um healthcheck para garantir que o container está rodando bem
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando para rodar a aplicação
# O server.address=0.0.0.0 é obrigatório no Docker para acessar de fora do container
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
