import os
import time
import json
import requests
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import numpy as np
# from TenantUnionPlus import *
# CSS: https://stackoverflow.com/questions/22259847/application-not-picking-up-css-file-flask-python

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file

client_secret = json.load(open('client_secret.json'))
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'TenantUnionPlus.db'),
    SECRET_KEY=client_secret['web']['client_secret'],
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('TENANT_UNION_PLUS_SETTINGS', silent=True)


# OAuth requires https, this is to silent the warning
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

## SEE: https://developers.google.com/identity/protocols/googlescopes
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['profile', 'email']
API_SERVICE_NAME = 'plus'
API_VERSION = 'v1'

# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
# app.secret_key = 'wBwhfdLNVp0pCQqL5lVIgmXf'
# from urllib import request
from geopy import geocoders
import random
# a=''
# b=''
# url = r'https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIzaSyDZNR0tka_TdxqMhxxkCbTbvcMJ-lwzgVY'
# res = request.urlopen(url)
# html = res.read().decode('utf-8')
# with open("latitude_longtitude.txt","w") as f:
#     f.write(html)
# file=open("latitude_longtitude.txt")
# line=file.readlines()
# a=line[58]
# b=line[59]
# file.close()
# a=a[23:32]
# b=b[23:32]
# print(a)
# print(b)

def geocode(address, geo_keys):
    g = geocoders.GoogleV3(api_key=random.choice(geo_keys))
    # g = geocoders.GoogleV3(api_key=geo_keys[0])
    place, (lat, lng) = g.geocode(address)
    return place, lat, lng

from bs4 import BeautifulSoup
def test():
    soup = BeautifulSoup(open("pag1.html"), 'html.parser')
    address = []
    bed = []
    bath = []
    rent = []
    url = []
    for link in soup.find_all('a'):
        URL = link.get('href')
        URL = "https://tenantunion.illinois.edu" + str(URL)
        br1 = link.findNext('br')
        property_type = br1.nextSibling
        br2 = property_type.findNext('br')
        Beds = br2.nextSibling
        br3 = Beds.findNext('br')
        Baths = br3.nextSibling
        br4 = Baths.findNext('br')
        Address = br4.nextSibling
        br5 = Address.findNext('br')
        Rent = br5.nextSibling
        Address = process_address(Address)
        Beds = process_beds(Beds)
        Baths = process_baths(Baths)
        Rent = process_rent(Rent)
        address.append(Address)
        bed.append(Beds)
        bath.append(Baths)
        rent.append(Rent)
        url.append(URL)

    return address, bed, bath, rent, url

def preprocess(string):
    string = str(string)
    string = string.replace('\n', '')
    string = string.replace('\t', '')
    string = string.replace(' ', '')
    return string

def process_address(Address):
    Address = preprocess(Address)
    Address = Address.replace('Address:', '')
    Address = Address.replace('61801', '')
    Address = Address.replace('61820', '')
    return Address

def process_beds(beds):
    beds = preprocess(beds)
    beds = beds.replace('Beds:', '')
    return beds

def process_baths(baths):
    baths = preprocess(baths)
    baths = baths.replace('Baths:', '')
    return baths

def process_rent(rent):
    rent = preprocess(rent)
    rent = rent.replace('Rent:', '')
    return rent



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])

    service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

    people_resource = service.people()
    people_document = people_resource.get(userId='me').execute()


    session['profile_pic'] = str(people_document['image']['url'])
    user_email = people_document['emails'][0][u'value'] # get user email
    user_email_splitted = user_email.split('@')
    user_netid = user_email_splitted[0]
    user_email_suffix = user_email_splitted[1]
    session['netid'] = user_netid

    if user_email_suffix != "illinois.edu":
        flash("You should use a illinois email to log in")
        return redirect(url_for('logout'))
    user_name = str(people_document['displayName']) #get user name
    session['name'] = user_name
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    session['credentials'] = credentials_to_dict(credentials)
    session['logged_in'] = True

    # DATABASE
    db = get_db()
    c = db.cursor()
    c.execute('SELECT count(*) FROM student WHERE NetID = ?', [user_netid])
    c_fetchone = c.fetchone()

    if c_fetchone[0] == 0 or c_fetchone == None:
        c.execute('INSERT INTO student (NetID, name) VALUES (?, ?)', [user_netid, user_name])
    db.commit()

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    requests.post('https://accounts.google.com/o/oauth2/revoke',
    params={'token': session['credentials']['token']},
    headers = {'content-type': 'application/x-www-form-urlencoded'})
    session.pop('logged_in', None)
    session.pop('credentials', None)
    session.pop('netid', None)
    session.pop('name', None)
    session.pop('profile_pic', None)
    flash('You were logged out')

    return redirect(url_for('home'))

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('login'))




def credentials_to_dict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}




@app.route('/')
def home():
    return render_template('home.html')

@app.route('/map')
def map():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT location, price, bedroom_num, bath_num, url, lat, lng from room")
    whole_profile = c.fetchall()

    address = []
    bed = []
    bath = []
    rent = []
    url = []
    lat = []
    lng = []

    for each_profile in whole_profile:
        ''' TODO: may need to update 'each_profile[5]' when adding more attribute! '''
        address.append(each_profile[0])
        rent.append(each_profile[1])
        bed.append(each_profile[2])
        bath.append(each_profile[3])
        url.append(each_profile[4])
        lat.append(each_profile[5])
        lng.append(each_profile[6])

    rent = process_rent1(rent)
    unit_rent = np.array(rent) / np.array(bed)
    length = len(address)
    return render_template('map.html', address = address, lat = lat, lng = lng, rent=rent, unit_rent = unit_rent, bed=bed, bath=bath, url=url, length=length)

def process_rent1(rent):
    for i, r in enumerate(rent):
        if type(r) == "int":
            pass
        else:
            r = str(r)
            if r[0] == '$':
                r = r[1:]
            rent[i] = int(r)
    return rent

@app.route('/recommend', methods=["GET", "POST"])
def recommend():
    if request.method == "GET":
        return render_template('questions.html')
    else: # POST
        year = request.form.get('year')
        direction = request.form.get('direction')
        gym = request.form.get('gym')
        cook = request.form.get('cook')
        commute = request.form.get('commute')
        study = request.form.get('study')
        pet = request.form.get('pet')
        # result should be a list of (lat, lng)
        result = recommend_result(year, direction, gym, cook, commute, study, pet)
        return redirect(url_for('result'), locations=result)



@app.route('/result', methods=['POST', 'GET'])
def result(locations):
    if request.method == 'POST':
        bed = request.form.getlist('bed')
        price = request.form.getlist('price')
        print(bed, price)
        return render_template('result.html', bed=bed, price=price)
    else:
        db = get_db()
        c = db.cursor()
        whole_profile = []
        for latLng in locations:
            c.execute("SELECT location, price, bedroom_num, bath_num, url, lat, lng from room WHERE lat = ? AND lng = ?", [latLng[0], latLng[1]])
            whole_profile.append(c.fetchone())

        address = []
        bed = []
        bath = []
        rent = []
        url = []
        lat = []
        lng = []

        for each_profile in whole_profile:
            ''' TODO: may need to update 'each_profile[5]' when adding more attribute! '''
            address.append(each_profile[0])
            rent.append(each_profile[1])
            bed.append(each_profile[2])
            bath.append(each_profile[3])
            url.append(each_profile[4])
            lat.append(each_profile[5])
            lng.append(each_profile[6])

        rent = process_rent(rent)
        unit_rent = np.array(rent) / np.array(bed)
        length = len(address)
        return render_template('result.html', address = address, lat = lat, lng = lng, rent=rent, unit_rent = unit_rent, bed=bed, bath=bath, url=url, length=length)

@app.route('/user/<netid>', methods=["GET", "POST"])
def profile(netid):
    if not session.get('logged_in'):
        flash("You need to log in to see your profile")
        abort(401)
    db = get_db()
    c = db.cursor()

    if request.method == 'POST':
        address = request.form.get('delete')
        c.execute('DELETE FROM likes WHERE location = ? AND NetID = ?', [address, netid])

    c.execute('SELECT * FROM student WHERE NetID = ?', [netid])
    user_profile = c.fetchone()
    name = user_profile[1]
    gender = user_profile[2]
    age = user_profile[3]
    major = user_profile[5]
    contact = user_profile[6]
    c.execute('SELECT count(*) FROM likes WHERE NetID = ?', [netid])
    c_fetchone = c.fetchone()
    if c_fetchone[0] == 0 or c_fetchone == None:
        location=''
        likeornot = 0
        db.commit()
    else:
        c.execute('SELECT location, likeornot, word  FROM likes WHERE NetID = ?', [netid])
        user_likes=c.fetchall()
        location=user_likes[0][0]
        likeornot=user_likes[0][1]
        word=user_likes[0][2]
        db.commit()

        return render_template('user_profile.html', netid=netid, name=name, \
                                gender=gender, age=age, major=major, contact=contact, \
                                profile_pic=session['profile_pic'], \
                                user_likes=user_likes)

@app.route('/user/<netid>/edit', methods=['GET', 'POST'])
def edit_user_profile(netid):
    if not session.get('logged_in'):
        flash("You need to log in to see your profile")
        abort(401)

    if request.method == 'POST':
        name = request.form.get('name', 'notSet')
        gender = request.form.get('gender', 'notSet')
        age = request.form.get('age', 0)
        major = request.form.get('major', 'notSet')
        contact = request.form.get('contact', 'notSet')

        db = get_db()
        c = db.cursor()
        c.execute('UPDATE student SET name = ?, \
                                      gender = ?, \
                                      age = ?, \
                                      major = ?, \
                                      mailbox = ? \
                                      WHERE NetID = ?', [name, gender, age, major, contact, netid])
        db.commit()
        return redirect(url_for('profile', netid=netid))
    else:
        return render_template("edit_user_profile.html", netid=netid, profile_pic=session['profile_pic'])

@app.route('/house/profile/<location>',methods=['GET', 'POST'])
def house_profile(location):
    session['location']=location
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM room WHERE location = ? ', ([location]))
    user_profile = c.fetchone()
    db.commit()

    if session.get('logged_in'):
        netid = session['netid']
        if request.method == 'POST':
            likeornot = request.form.get('likeornot', None)
            word = request.form.get('word',None)
            # print(type(likeornot))
            # print(str(likeornot))
            if str(likeornot) != '':
                db = get_db()
                c = db.cursor()
                c.execute('SELECT count(*) FROM likes WHERE location = ? AND NetID = ?', [location,netid])
                c_fetchone = c.fetchone()
                if c_fetchone[0] == 0 or c_fetchone == None: # if the user has not comment this page yet
                    c.execute('INSERT INTO likes (location,NetID,word,likeornot) VALUES (?, ?, ?, ?)', [location, netid, word, likeornot])
                else: # if the user has commented the page
                    c.execute('UPDATE likes SET likeornot = ?, word = ?\
                                WHERE location = ? AND NetID = ?', [likeornot , word, location , netid])
                db.commit()
            else:
                c.execute('SELECT count(*) FROM likes WHERE location = ? AND NetID = ?', [location,netid])
                c_fetchone = c.fetchone()
                if c_fetchone[0] == 0 or c_fetchone == None:
                    likeornot = 0
                    word = ''
                    db.commit()
                else:
                    c.execute('SELECT likeornot, word FROM likes WHERE location = ? AND  NetID = ?', ([location,netid]))
                    comment = c.fetchone()
                    likeornot = comment[0]
                    word = comment[1]
                    db.commit()
        else: # GET
            c.execute('SELECT count(*) FROM likes WHERE location = ? AND NetID = ?', [location,netid])
            c_fetchone = c.fetchone()
            if c_fetchone[0] == 0 or c_fetchone == None:
                likeornot = 0
                word = ''
                db.commit()
            else:
                c.execute('SELECT likeornot, word FROM likes WHERE location = ? AND  NetID = ?', ([location,netid]))
                comment = c.fetchone()
                likeornot = comment[0]
                word = comment[1]
                db.commit()
        c.execute('SELECT * FROM likes WHERE location = ?', ([location]))
        allcomments=c.fetchall()
        db.commit()
        c.execute('SELECT AVG(likeornot) FROM likes WHERE location = ?', ([location]))
        avgscore=c.fetchone()
        avgscore=avgscore[0]
        db.commit()
        c.execute('SELECT count(*)  FROM likes WHERE location = ?', ([location]))
        count=c.fetchone()
        count=count[0]
        db.commit()
        return render_template('house_profile.html',location=location,likeornot=likeornot,word=word,allcomments=allcomments,avgscore=avgscore,count=count)
    else:
        c.execute('SELECT * FROM likes WHERE location = ?', ([location]))
        allcomments=c.fetchall()
        db.commit()
        c.execute('SELECT AVG(likeornot) FROM likes WHERE location = ?', ([location]))
        avgscore=c.fetchone()
        avgscore=avgscore[0]
        db.commit()
        c.execute('SELECT count(*)  FROM likes WHERE location = ?', ([location]))
        count=c.fetchone()
        count=count[0]
        db.commit()
        return render_template('house_profile.html',location=location,allcomments=allcomments,avgscore=avgscore,count=count)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    address, bed, bath, rent, url = test()
    lat, lng = init_house_lat_lng(address)
    c = db.cursor()
    with app.open_resource('TenantUnionPlus.sql', mode='r') as f:
        c.executescript(f.read())

    for i, URL in enumerate(url):
        c.execute("INSERT INTO room(location, price, bedroom_num, bath_num, url, lat, lng) VALUES (?, ?, ?, ?, ?, ?, ?)", \
                [address[i], rent[i], bed[i], bath[i], url[i], lat[i], lng[i]])
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def init_house_lat_lng(address):
    maps_apis = client_secret['map']
    geo_keys = [maps_apis['api1'], maps_apis['api2']]

    lat = []
    lng = []
    for addr in address:
        addr_tuple = geocode(addr, geo_keys)
        lat.append(addr_tuple[1])
        lng.append(addr_tuple[2])

    return lat, lng

def update_house():
    address, bed, bath, rent, url = test()
    db = get_db()
    c = db.cursor()
    ''' TRIGGER? '''
    # check house information deletion
    c.execute("SELECT location, price, bedroom_num, bath_num, url from room")
    whole_profile = c.fetchall()
    for each_profile in whole_profile:
        ''' TODO: may need to update 'each_profile[5]' when adding more attribute! '''
        URL_db = each_profile[4]
        if URL_db in url:
            pass
        else:   # house information was deleted from TenantUnion
            c.execute("DELETE FROM romm WHERE url = ?", [URL_db])

    # check house information update
    for i, URL in enumerate(url):
        c.execute("SELECT * FROM room WHERE url = ?", [URL])
        house_profile = c.fetchone()
        if house_profile == None or houseProfile == 0: # new house added
            c.execute("INSERT INTO room(location, price, bedroom_num, bath_num, url) VALUES (?, ?, ?, ?, ?)", \
                        [address[i], rent[i], bed[i], bath[i], url[i]])
            init_house_lat_lng(address[i])

        else: #check whether house price get updated
            c.execute("SELECT price FROM room WHERE url = ?", [URL])
            price_info = c.fetchone()[0]
            if str(price_info) != rent[i]:
                c.execute("UPDATE room SET price = ? WHERE url = ?", [rent[i], url[i]])
    db.commit()


@app.cli.command('update')
def update_house_command():
    '''update house profile'''
    update_house()
    print('House profile update successfully')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
