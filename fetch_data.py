import requests
import json
from pathlib import Path

def fetch_results(checkpoint_id=2191864):
    """Récupérer les résultats depuis l'API"""
    url = "https://api.resultats-live.com/graphql"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Host": "api.resultats-live.com",
        "Origin": "https://live.run-athle-03.fr",
        "Referer": "https://live.run-athle-03.fr/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:138.0) Gecko/20100101 Firefox/138.0"
    }

    query = """
    query getResults($checkpointId: Int!, $category: String, $gender: String, $search: String, $limit: Int, $offset: Int) {
      totalResults: resultsByCheckpointIdCount(
        id: $checkpointId
        category: $category
        gender: $gender
      )
      results: resultsByCheckpointId(
        id: $checkpointId
        category: $category
        gender: $gender
        search: $search
        limit: $limit
        offset: $offset
      ) {
        id
        time
        ranking
        gender_ranking
        category_ranking
        checkpoint_id
        participant {
          id
          firstname
          lastname
          birthdate
          gender
          country
          club
          category
          category_shortname
          bib_number
          __typename
        }
        __typename
      }
    }
    """

    variables = {
        "checkpointId": checkpoint_id,
        "category": None,
        "gender": None,
        "limit": 3000,
        "offset": 0
    }

    payload = {
        "operationName": "getResults",
        "variables": variables,
        "query": query
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Sauvegarder les données
        with open("race_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("Données récupérées et sauvegardées avec succès!")
        return data
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {str(e)}")
        return None

if __name__ == "__main__":
    fetch_results() 