import requests
from dotenv import load_dotenv
import os

load_dotenv()
MOVIE_API_URL = "https://api.themoviedb.org/3/search/movie"

movie_title = "the killers of the moon flower"
response = requests.get(
    url=MOVIE_API_URL,
    params={
        "query": movie_title,
        "page": 1,
        "language": "en-US",
        "include_adult": "false"
    },
    headers={
            "accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('MOVIE_API_TOKEN')}"
        }
)
response.raise_for_status()
result = response.json()
print(result)
movie_details = result["results"]
print(movie_details)
