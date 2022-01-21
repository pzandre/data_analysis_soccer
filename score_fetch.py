import requests
import sys
import time
import os

from team_data import get_team_last_matches_from_match, calc_last_5_matches_win_rate
from datetime import datetime


COUNTRIES = ["germany", "greece", "england", "italy", "spain"]

MIN_WIN_RATE = float(sys.argv[1])
MIN_ELAPSED_TIME = float(sys.argv[2])

url = "https://livescore-football.p.rapidapi.com/soccer/live-matches"

querystring = {"timezone_utc": "-3:00"}

headers = {
    "x-rapidapi-host": os.getenv('RAPIDAPI_HOST'),
    "x-rapidapi-key":  os.getenv('RAPIDAPI_KEY')
}

print("A")
response = requests.request("GET", url, headers=headers, params=querystring)
print("B")
response_data_list = response.json().get("data")
print("C")
# print(response_data_list)


def filter_by_country(country_code, data_json_list):
    filtered_list = []
    for data in data_json_list:
        if data.get("country_code") == country_code:
            filtered_list.append(data)
    return filtered_list


def filter_one_difference_goal(data_json_list):
    filtered_list = []
    for data in data_json_list:
        list_of_matches_in_league = data.get("matches")
        for match in list_of_matches_in_league:
            team1_score = match.get("score").get("full_time").get("team_1")
            team2_score = match.get("score").get("full_time").get("team_2")

            team1_id = match.get("team_1").get("id")
            team2_id = match.get("team_2").get("id")

            match_id = match.get("match_id")

            # upset situation
            if abs(int(team1_score) - int(team2_score)) == 1:
                losing_team_id = team1_id if team1_score < team2_score else team2_id
                try:
                        losing_team_last_5_matches_outcomes = (
                        get_team_last_matches_from_match(match_id, losing_team_id)
                    )
                except TypeError:
                    continue

                win_rate_last_5_matches = calc_last_5_matches_win_rate(
                    losing_team_last_5_matches_outcomes
                )

                if win_rate_last_5_matches > MIN_WIN_RATE:
                    filtered_list.append(data)

    return filtered_list


# print(response_data_list)

# print(filter_one_difference_goal(response_data_list))

print(f"having win_rate greater than {MIN_WIN_RATE}")
for i in filter_one_difference_goal(response_data_list):
    for j in i.get("matches"):
        try:
            fmt = "%Y%m%d%H%M%S"
            start_time = datetime.strptime(str(j["time"]["start"]), fmt)
            time_since_start = datetime.now() - start_time
            minutes_since_start = (time_since_start.total_seconds())/60                                                                  
            
            if minutes_since_start > MIN_ELAPSED_TIME:
                team1_name = j["team_1"]["name"]
                team1_country = j["team_1"]["country"]
                team2_name = j["team_2"]["name"]
                team2_country = j["team_2"]["country"]
                print(f"{team1_name} X {team2_name}")
        except Exception as e:
            print(e)
