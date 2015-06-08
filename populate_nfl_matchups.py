#!/usr/bin/python

import nflgame
import datetime
from mysite.nflbase import models as nbmodels
from mysite.nflsurvivor import models as nsmodels


def run_population():
    season = nbmodels.Season.objects.latest('start_date')

    for week_num in range(1,18):
        week_matchs = nflgame._search_schedule(datetime.datetime.today().year,week=week_num)
        for match in week_matchs:
            home_team = nbmodels.Team.objects.get(abbreviation=match['home'])
            away_team = nbmodels.Team.objects.get(abbreviation=match['away'])
            week = 'week' + str(week_num)
            nsmodels.Matchup.objects.create(season=season,away_team=away_team,home_team=home_team,week=week)





