import datetime
import json
import time
from typing import List
import dateparser
from pydantic import BaseModel
import requests
from icecream import ic


class MozgoUserLogin(BaseModel):
    token_type: str
    expires_in: int
    access_token: str
    refresh_token: str


class MozgoTeams(BaseModel):
    city: str
    city_id: int
    id: int
    name: str


class MozgoCaptain(BaseModel):
    name: str
    phone: str
    teams: List[MozgoTeams]


class MozgoEvent(BaseModel):
    uuid: str
    address: str
    game_type: str
    place: str
    played_at: str
    registration_at: str


class MozgoEventList(BaseModel):
    __root__: List[MozgoEvent]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


class Mozgo:
    def __init__(self, login, password):
        assert type(login) == str, 'login must be string'
        assert type(password) == str, 'password must be string'
        self.login = login
        self.password = password
        self.current_team_index = None
        self.current_event_index = None
        self.players_count = None

        url_login = "https://api.base.mozgo.com/login"

        payload_login = {'email': self.login, 'password': self.password}
        headers_login = {'Content-Type': 'application/json'}

        response_login = requests.request(
            "POST", url_login, headers=headers_login, json=payload_login)

        self.user = MozgoUserLogin(**response_login.json())

        if response_login.status_code == 200:
            print('Login success')
        else:
            print('Login failed')

    def __get_team_id_list(self):
        # TODO add check of current team index (<= len(self.teams.teams))
        url_team_id_list = 'https://api.base.mozgo.com/players/me'

        headers_team_id_list = {
            'Authorization': f'{self.user.token_type} {self.user.access_token}',
            'Content-Type': 'application/json'
        }

        response_team_id_list = requests.request(
            "GET", url_team_id_list, headers=headers_team_id_list)

        self.teams = MozgoCaptain(**response_team_id_list.json())

        print('Available teams:')
        for i, j in enumerate(self.teams.teams):
            print(f'{i}. {j.name} ({j.city})')
        print('Enter the number to select the team:')
        self.current_team_index = int(input())
        print('Enter the number of players:')
        self.players_count = int(input())

    def __get_event_list(self):
        # TODO add check of current event index (<= len(self.event))

        url_event_list = f'https://api.base.mozgo.com/events/dates/{self.teams.teams[self.current_team_index].city_id}'

        headers_event_list = {
            'Authorization': f'{self.user.token_type} {self.user.access_token}',
            'Content-Type': 'application/json'
        }

        response_event_list = requests.request(
            "GET", url_event_list, headers=headers_event_list)

        self.event = MozgoEventList(__root__=response_event_list.json())
        print('Available games:')
        for i, j in enumerate(self.event):
            print(f'{i}. {j.game_type} ({j.played_at})')
        print('Enter the number to select the game:')
        self.current_event_index = int(input())

    def register_to_game(self):
        # TODO add time check
        if self.current_team_index is None:
            self.__get_team_id_list()
        if self.current_event_index is None:
            self.__get_event_list()

        now = datetime.datetime.now()
        aim = dateparser.parse(self.event[self.current_event_index].registration_at)
        while now < aim:
            now = datetime.datetime.now()
            print((aim - now), 'remaining')
            # ic((aim - now))
            # ic((aim - now).days * 86400 + (aim - now).seconds)
            est_time = (aim - now).days * 86400 + (aim - now).seconds + 1
            if est_time > 0:
                time.sleep(est_time)
        # ic(now)
        # ic(aim)
        # ic(now > aim)

        url_reg = "https://api.base.mozgo.com/players/applications"

        payload_reg = {'captain_email': self.login,
                       'captain_name': self.teams.name,
                       'captain_phone': self.teams.phone,
                       'comment': '',
                       'event_day_id': self.event[self.current_event_index].uuid,
                       'play_for_first_time': False,
                       'player_count': self.players_count,
                       'promocode': '',
                       'sms': '',
                       'team_id': self.teams.teams[self.current_team_index].id}

        headers_reg = {
            'Authorization': f'{self.user.token_type} {self.user.access_token}',
            'Content-Type': 'application/json'
        }

        response_reg = requests.request(
            "POST", url_reg, headers=headers_reg, json=payload_reg)

        if response_reg.status_code == 201:
            print('You have registered to the game')
        else:
            print('Registration failed')
        return response_reg.status_code
