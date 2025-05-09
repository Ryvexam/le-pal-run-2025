FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de l'application
COPY requirements.txt .
COPY app.py .
COPY fetch_data.py .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Récupérer les données pendant le build
RUN python fetch_data.py && \
    # Vérifier que le fichier JSON a été créé
    test -f race_data.json || (echo "Erreur: race_data.json n'a pas été créé" && exit 1)

# Copier le fichier JSON généré
COPY race_data.json .

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Vérification de santé
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Lancer l'application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 