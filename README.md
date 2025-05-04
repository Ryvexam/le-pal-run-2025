# Analyse des Résultats de Course

Application Streamlit pour analyser les résultats de courses.

## Fonctionnalités

- Analyse des performances par catégorie d'âge
- Statistiques détaillées par club
- Visualisation des temps moyens et médians
- Filtrage par genre, catégorie et club
- Podium des meilleurs clubs

## Prérequis

- Docker installé sur votre machine

## Installation et Lancement

### Localement

1. Cloner le dépôt :
```bash
git clone <url-du-depot>
cd <nom-du-depot>
```

2. Construire l'image Docker :
```bash
docker build -t course-analyzer .
```

3. Lancer le conteneur :
```bash
docker run -p 8501:8501 course-analyzer
```

4. Accéder à l'application :
Ouvrez votre navigateur et allez à l'adresse : http://localhost:8501

### Depuis Docker Hub

```bash
docker pull <votre-username>/course-analyzer:latest
docker run -p 8501:8501 <votre-username>/course-analyzer:latest
```

## Déploiement Automatique

L'application est configurée pour un déploiement automatique sur Docker Hub via GitHub Actions. Pour configurer :

1. Créez un compte sur [Docker Hub](https://hub.docker.com/)
2. Créez un token d'accès dans Docker Hub (Account Settings > Security > New Access Token)
3. Ajoutez les secrets suivants dans votre dépôt GitHub (Settings > Secrets and variables > Actions) :
   - `DOCKERHUB_USERNAME` : Votre nom d'utilisateur Docker Hub
   - `DOCKERHUB_TOKEN` : Le token d'accès créé

Le workflow se déclenchera automatiquement à chaque push sur la branche main.

## Structure du Projet

- `app.py` : Application Streamlit principale
- `requirements.txt` : Dépendances Python
- `Dockerfile` : Configuration Docker
- `.github/workflows/docker-publish.yml` : Configuration du déploiement automatique
- `race_data.json` : Cache des données de course

## Utilisation

1. L'application se connecte automatiquement à l'API des résultats
2. Utilisez les filtres en haut de la page pour affiner l'analyse
3. Consultez les différentes sections pour voir les statistiques et visualisations

## Notes

- Les données sont mises en cache localement pour éviter de surcharger l'API
- L'application met à jour automatiquement les données si nécessaire 