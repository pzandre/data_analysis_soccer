import requests
import os

url = "https://livescore-football.p.rapidapi.com/soccer/leagues-by-country"

querystring = {"country_code":"england"}

headers = {
    "x-rapidapi-host": os.getenv('RAPIDAPI_HOST'),
    "x-rapidapi-key":  os.getenv('RAPIDAPI_KEY')
}

response = requests.request("GET", url, headers=headers, params=querystring)
response_data_as_list = response.json().get('data')

for i in response_data_as_list:
    print(i.get('league_code'))



