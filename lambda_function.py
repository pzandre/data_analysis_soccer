import requests
import os
import json
from data_analysis_soccer.team_data import get_team_last_matches_from_match, calc_last_5_matches_win_rate
from datetime import datetime


COUNTRIES = ["germany", "greece", "england", "italy", "spain"]

MIN_WIN_RATE = 0.5
MIN_ELAPSED_TIME = 10

url = "https://livescore-football.p.rapidapi.com/soccer/live-matches"

querystring = {"timezone_utc": "-3:00"}

headers = {
    "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
}

print("Starting request...")
response = requests.request("GET", url, headers=headers, params=querystring)
print("Getting request json data...")
response_data_list = response.json().get("data")
print("Calculating hot tips...")


def filter_by_country(country_code, data_json_list):
    filtered_list = []
    for data in data_json_list:
        if data.get("country_code") == country_code:
            filtered_list.append(data)
    return filtered_list


def filter_one_difference_goal(data_json_list):
    filtered_list = []
    for data in data_json_list:
        list_of_all_matches = data.get("matches")
        for match in list_of_all_matches:
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
                except:
                    continue

                win_rate_last_5_matches = calc_last_5_matches_win_rate(
                    losing_team_last_5_matches_outcomes
                )

                if win_rate_last_5_matches > MIN_WIN_RATE:
                    filtered_list.append(match)

    return filtered_list


# print(response_data_list)

# print(filter_one_difference_goal(response_data_list))

def lambda_handler(event, handler):
    matches = []
    for i in filter_one_difference_goal(response_data_list):
        # for j in i.get("matches"):
        try:
            fmt = "%Y%m%d%H%M%S"
            start_time = datetime.strptime(str(i["time"]["start"]), fmt)
            time_since_start = datetime.now() - start_time
            minutes_since_start = (time_since_start.total_seconds()) / 60
    
            if minutes_since_start > MIN_ELAPSED_TIME:
                team1_name = i["team_1"]["name"]
                team2_name = i["team_2"]["name"]
    
                team1_score = i["score"]["full_time"]["team_1"]
                team2_score = i["score"]["full_time"]["team_2"]

                matches.append(
                    f"{team1_name} having {team1_score} goals X {team2_name} having {team2_score} goals"
                )
        except Exception as e:
            matches.append(f"Error while printing hot tips {e}")
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(matches)
    }
