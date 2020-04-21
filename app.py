from flask import Flask, render_template, json, request
import requests

app = Flask(__name__)


@app.route("/")
def index():

    global covidglobal, countrylist, globalstats, covid

    covid = requests.get("https://api.covid19api.com/summary")
    covid = covid.json()
    
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

    return render_template('index.html', covidglobal=covidglobal, countrylist=countrylist, globalstats=globalstats)

@app.route("/search")
def search():
    for key,value in covid.items():
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
                
    return render_template('index.html', covidglobal=covidglobal, countrylist=countrylist, globalstats=globalstats)


@app.route("/countrystats/<string:countryname>")
def countrystats(countryname):
    
    for key,value in covid.items():
        if key == "Countries":
            for val in value:
                statistics = [val for val in value if countryname == val['Country']][0]
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
    return render_template('country.html', statistics=statistics , globalstats=globalstats)


def calcul(a,b):
    """ 
        Function to calc the stats
    """
    return (a/b)*100

if __name__ == '__main__':
    app.run()
    
    