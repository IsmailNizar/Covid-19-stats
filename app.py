from flask import Flask, render_template, json, request, redirect, url_for
import requests
import pygeoip, json, os, time
from datetime import datetime
import datetime as dt
import base64

app = Flask(__name__)

# load the file in memory everytime the webserver is restarted
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
geo = pygeoip.GeoIP(os.path.join(BASE_DIR, 'GeoLiteCity.dat'))

@app.route("/")
def index():

    global covidglobal, countrylist, globalstats
    totaldates = []
    totalcases = []

    globalstatsDaybyday = requests.get("https://covid19-update-api.herokuapp.com/api/v1/cases/graphs/totalCases")
    globalstatsDaybyday = globalstatsDaybyday.json()
    covid = requests.get("https://api.covid19api.com/summary")
    covid = covid.json()

    totaldates = globalstatsDaybyday['graph']['categories']
    totalcases = globalstatsDaybyday['graph']['data']

    for key,value in covid.items():
        if key =="Global":
            covidglobal = value
            still = covidglobal['TotalConfirmed'] -(covidglobal['TotalDeaths'] + covidglobal['TotalRecovered'])
            covidglobal['still']=still
        if key == "Countries":
            for val in value:
                stat = calcul(val['TotalConfirmed'],covidglobal['TotalConfirmed'])
                val['stats']=stat
            
            query = request.args.get('country')
            if not query:
                countrylist = sorted(value, key=lambda colonnes: colonnes['TotalConfirmed'],reverse = True)
            else :
                filterlist = [val for val in value if query.capitalize() in val['Country']]
                countrylist = sorted(filterlist, key=lambda colonnes: colonnes['TotalConfirmed'],reverse = True)

        deathstat = calcul(covidglobal['TotalDeaths'],covidglobal['TotalConfirmed'])
        recoveredstat = calcul(covidglobal['TotalRecovered'],covidglobal['TotalConfirmed'])
        stillstat = calcul(still,covidglobal['TotalConfirmed'])
        globalstats = {
            'stillstat' : "%.2f" % stillstat,
            'deathstat' : "%.2f" % deathstat,
            'recoveredstat' : "%.2f" % recoveredstat
        }

    return render_template('index.html',day=globalstatsDaybyday, covidglobal=covidglobal, countrylist=countrylist, globalstats=globalstats,totaldates=totaldates, totalcases=totalcases)

@app.route("/search")
def search():
            
    query = request.args.get('country')               
    return redirect(url_for('index',country=query))

@app.route("/countrystats/<string:countryname>")
def countrystats(countryname):
    months = []
    totalcases = []
    covid = requests.get("https://api.covid19api.com/summary")

    contryStats = requests.get("https://api.covid19api.com/dayone/country/"+ countryname)

    if contryStats.status_code == 200 :
        a = contryStats.status_code
        covid = covid.json()
        contryStats = contryStats.json()
        for everyStat in contryStats:
            datess = datetime.strptime(everyStat['Date'],"%Y-%m-%dT%H:%M:%SZ")
            months.append(datess)
            totalcases.append(everyStat["Confirmed"])
        for key,value in covid.items():
            if key == "Countries":
                for val in value:
                    statistics = [val for val in value if countryname == val['Country']][0]
                    statistics['Dates'] = datetime.strptime(statistics['Date'],"%Y-%m-%dT%H:%M:%SZ")
                    still = statistics['TotalConfirmed'] -(statistics['TotalDeaths'] + statistics['TotalRecovered'])
                    statistics['still']=still
        deathstat = calcul(statistics['TotalDeaths'],statistics['TotalConfirmed'])
        recoveredstat = calcul(statistics['TotalRecovered'],statistics['TotalConfirmed'])
        stillstat = calcul(still,statistics['TotalConfirmed'])
        globalstats = {
            'stillstat' : "%.2f" % stillstat,
            'deathstat' : "%.2f" % deathstat,
            'recoveredstat' : "%.2f" % recoveredstat
        }
        # for i in months:
        #     a = i[0:16]
        #     x.append(a)
        return render_template('country.html', statistics=statistics , globalstats=globalstats, contryStats=contryStats, months=months,totalcases=totalcases, a=a)

    else:
        error = contryStats.status_code
        return redirect (url_for('index',error=error))

def calcul(a,b):
    """ 
        Function to calc the stats
    """
    return (a/b)*100

if __name__ == '__main__':
    app.run()
    
    