FROM python:3.9-slim

#Defina o diretório de trabalho
WORKDIR /app

#Copie os arquivos de requisitos
COPY requirements.txt requirements.txt

#Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

#Copie o código do aplicativo
COPY src /app

#Instale as dependências do sistema (necessário para o DevContainer)
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

#Defina o usuário padrão (necessário para o DevContainer)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

#Comando para iniciar o aplicativo Flask
CMD ["flask", "run", "--host=0.0.0.0"]