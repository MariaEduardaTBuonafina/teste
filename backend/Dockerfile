# Imagem Python leve como base
FROM python:3.11-slim

# Pasta de trabalho dentro do container
WORKDIR /app

# Copiamos o requirements.txt ANTES do código — otimização de cache do Docker:
# se só o app.py mudar, o Docker não reinstala as dependências
COPY requirements.txt .

# Instalamos as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos o restante do código
COPY . .

# Porta que o container vai expor
EXPOSE 5000

# Comando de inicialização
CMD ["python", "app.py"]