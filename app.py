from flask import Flask, render_template, json, request
import requests
import pygeoip, json, os, time
from datetime import datetime
import base64

app = Flask(__name__)

# load the file in memory everytime the webserver is restarted
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
geo = pygeoip.GeoIP(os.path.join(BASE_DIR, 'GeoLiteCity.dat'))

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


@app.route('/pixel.gif', methods=['POST', 'GET'])
def pixel_tracker():
    # <img src="https//<<YOUR ACCOUNT>>.pythonanywhere.com//pixel.gif?page=somewhere" style="width: 1px; height: 1px" />
    origin_page = 'nowhere'
    address = 'nowhere'
    client_ip = ''

    if 'page' in request.args:
        origin_page = request.args.get('page')

        # visitor IP
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        # visitor referrer
        referrer = request.headers.get("Referer")

        # location of visitor - wont' work on free PythonAnywhere accounts
        # url = 'https://freegeoip.app/json/{}'.format(client_ip)
        # r = requests.get(url)
        # j = json.loads(r.text)

        # https://pygeoip.readthedocs.io/en/v0.3.2/index.html
        # https://github.com/walchko/Python/blob/master/network_python/geolocate/GeoLiteCity.dat
        geo_data = geo.country_name_by_addr(client_ip)

    # encoded pixel image https://github.com/sethblack/python-flask-pixel-tracking/blob/master/pfpt/main.py
    pixel_data = base64.b64decode("R0lGODlhAQABAIAAAP8AAP8AACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==")

    # log traffic to file
    st = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    # save to file and send thank you note
    with open("pixel-tracker.csv","a") as myfile:
        myfile.write('Timestamp: ' + st + ' origin_page:' + origin_page +
            ' client_ip: ' + client_ip + ' referrer:' + referrer + ' geo:' + str(geo_data) + '\n')

    return Response(pixel_data, mimetype="image/gif")

def calcul(a,b):
    """ 
        Function to calc the stats
    """
    return (a/b)*100

if __name__ == '__main__':
    app.run()
    
    