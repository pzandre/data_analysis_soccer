import requests
import os

url = "https://livescore-football.p.rapidapi.com/soccer/match-h2h"


headers = {
    "x-rapidapi-host": os.getenv('RAPIDAPI_HOST'),
    "x-rapidapi-key":  os.getenv('RAPIDAPI_KEY')
}


def get_h2h_data(match_id):
    querystring = {"match_id": match_id}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()



#print(get_h2h_data('267554'))

def get_team_last_matches_from_match(match_id, team_id):
    h2h_data = get_h2h_data(match_id)['data']
     
    if h2h_data['team_1']['id'] == team_id:
        team_last_matches_as_list = h2h_data.get('team_1').get('last_matches') 
    else:
        team_last_matches_as_list = h2h_data.get('team_2').get('last_matches') 

    match_outcomes_team_1 = [] 
    for match in team_last_matches_as_list:
        # team1 and team2 are teams that played in this particular past match
        # team1 and team2 from one particular match can be different from another 
        
        id_team1_from_this_game = match.get('team_1').get('id') 
        id_team2_from_this_game = match.get('team_2').get('id')
        
        try:
            score_team1_from_this_game = int(match['score']['team_1']) 
            score_team2_from_this_game = int(match['score']['team_2']) 
        except Exception as e:
            print(f" Unable to get the score {e}")
            continue
 

        if score_team1_from_this_game > score_team2_from_this_game:
            score_json = {id_team1_from_this_game:'W', id_team2_from_this_game: 'L'}
        elif score_team1_from_this_game < score_team2_from_this_game:
            score_json = {id_team1_from_this_game:'L', id_team2_from_this_game: 'W'}
        else:
            score_json = {id_team1_from_this_game:'D', id_team2_from_this_game: 'D'}
      
        match_outcomes_team_1.append(score_json.get(team_id))
      #  print(score_json)     
    return match_outcomes_team_1
 

def calc_last_5_matches_win_rate(match_outcomes_list):
    # we dont wanna teams that does not have stats with less than 5 last match
    if len(match_outcomes_list) < 5:
        return -1

    last_5_matches_outcome = match_outcomes_list[0:5]
    win_rate = last_5_matches_outcome.count('W')/len(last_5_matches_outcome) 
    return  win_rate




         

        


    