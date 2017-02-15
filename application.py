import datetime
import requests
import requests_cache
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template

application = Flask(__name__)

# Create a config.py file with API_TOKEN = '' and CACHE_TTL = int
application.config.from_object('config')

apitoken = application.config["API_TOKEN"]
cache_ttl = application.config["CACHE_TTL"]

requests_cache.install_cache('football_data_cache', backend='sqlite',
                             expire_after=cache_ttl)

headers = {'X-Auth-Token': apitoken, 'X-Response-Control': 'minified'}
url = 'http://api.football-data.org/v1/'


@application.route('/')
def getCompetitions():
    requeststring = "/competitions/"
    r = requests.get(url + requeststring, headers=headers)
    response = r.json()
    output = {}
    for competition in response:
        output[competition['id']] = {'caption': competition['caption'],
                                     'league': competition['league']}
    return render_template('index.html', content=output)


@application.route('/league/<league>')
def getTeams(league):
    requeststring = "/competitions/" + str(league) + "/teams"
    r = requests.get(url + requeststring, headers=headers)
    response = r.json()
    output = {}
    for team in response['teams']:
        output[team['id']] = team['name']
    return render_template('teamlist.html', content=output)


@application.route('/team/<team>')
def printNextMatch(team):
    today = str(datetime.date.today())
    nextMonth = str(datetime.date.today() + relativedelta(months=12))
    requeststring = "/teams/" + str(team) + "/fixtures?timeFrameStart=" +\
                    today + "&timeFrameEnd=" + nextMonth
    r = requests.get(url + requeststring, headers=headers)
    response = r.json()
    output = {}
    if response['count'] == 0:
        return("No Fixture in the next month")
    else:
        nextDate = response['fixtures'][0]['date']
        nextAwayTeam = response['fixtures'][0]['awayTeamName']
        nextHomeTeam = response['fixtures'][0]['homeTeamName']
        output['nextDate'] = nextDate
        output['nextHomeTeam'] = nextHomeTeam
        output['nextAwayTeam'] = nextAwayTeam
        return render_template('fixture.html', content=output)


if __name__ == "__main__":
    application.run()
