from icecream import ic
import requests
import json


class Mozgo:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.team_list = []
        self.event_list = []

        url_login = "https://api.base.mozgo.com/login"

        payload_login = {'email': self.login, 'password': self.password}
        headers_login = {'Content-Type': 'application/json'}

        response_login = requests.request(
            "POST", url_login, headers=headers_login, json=payload_login)

        self.login_token_type = response_login.json()['token_type']
        self.login_expires_in = response_login.json()['expires_in']
        self.login_access_token = response_login.json()['access_token']
        self.login_refresh_token = response_login.json()['refresh_token']

        if response_login.status_code == 200:
            print('Login success')
        else:
            print('Login failed')

    def get_team_id_list(self):
        url_team_id_list = 'https://api.base.mozgo.com/players/me'

        headers_team_id_list = {
            'Authorization': f'{self.login_token_type} {self.login_access_token}',
            'Content-Type': 'application/json'
        }

        response_team_id_list = requests.request(
            "GET", url_team_id_list, headers=headers_team_id_list)

        response_team_id_list_dict = response_team_id_list.json()
        self.captain_name = response_team_id_list_dict['name']
        self.captain_phone = response_team_id_list_dict['phone']

        for i in range(len(response_team_id_list_dict['teams'])):
            self.team_list.append(dict(city=response_team_id_list_dict['teams'][i]['city'],
                                       city_id=response_team_id_list_dict['teams'][i]['city_id'],
                                       team_id=response_team_id_list_dict['teams'][i]['id'],
                                       team_name=response_team_id_list_dict['teams'][i]['name']))

    def get_event_list(self, city_id):
        url_event_list = f'https://api.base.mozgo.com/events/dates/{city_id}'

        headers_event_list = {
            'Authorization': f'{self.login_token_type} {self.login_access_token}',
            'Content-Type': 'application/json'
        }

        response_event_list = requests.request(
            "GET", url_event_list, headers=headers_event_list)

        response_event_list_dict = response_event_list.json()

        for i in range(len(response_event_list_dict)):
            self.event_list.append(dict(game_topic=response_event_list_dict[i]['game_topic'],
                                        event_id=response_event_list_dict[i]['uuid'],
                                        place=response_event_list_dict[i]['place'],
                                        played_at=response_event_list_dict[i]['played_at']))

    def register_to_game(self, game_id, team_id, player_count):
        self.get_team_id_list()

        url_reg = "https://api.base.mozgo.com/players/applications"

        payload_reg = {'captain_email': self.login,
                       'captain_name': self.captain_name,
                       'captain_phone': self.captain_phone,
                       'comment': '',
                       'event_day_id': game_id,
                       'play_for_first_time': False,
                       'player_count': player_count,
                       'promocode': '',
                       #    'roistat_first_visit': '634805',
                       #    'roistat_visit': '',
                       'sms': '',
                       'team_id': team_id}

        headers_reg = {
            'Authorization': f'{self.login_token_type} {self.login_access_token}',
            'Content-Type': 'application/json'
        }

        response_reg = requests.request(
            "POST", url_reg, headers=headers_reg, json=payload_reg)

        if response_reg.status_code == 201:
            print('You have registered to the game')
        else:
            print('Registration failed')
        return response_reg.status_code

        # ic(response_reg.status_code)
        # ic(response_reg.text)
