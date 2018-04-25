import os
import time
import json
import requests
import numpy as np
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleplaces import GooglePlaces, types, lang
from readlocation import geocode
from crawler import get_house_info, test
# from rate import *
# from TenantUnionPlus import *
# CSS: https://stackoverflow.com/questions/22259847/application-not-picking-up-css-file-flask-python
# http://flask.pocoo.org/docs/0.12/tutorial/setup/#tutorial-setup
# http://flask.pocoo.org/docs/0.12/patterns/packages/#larger-applications
# http://flask.pocoo.org/docs/0.12/appcontext/#app-context
# http://flask.pocoo.org/docs/0.12/testing/#testing
# http://flask.pocoo.org/docs/0.12/quickstart/#sessions
# https://bootsnipp.com/snippets/featured/average-user-rating-rating-breakdown
# https://demos.creative-tim.com/material-kit/index.html?_ga=2.196049324.1610237639.1521848104-1497747171.1521848104

# http://flask.pocoo.org/docs/0.10/deploying/cgi/
# http://thelazylog.com/install-python-as-local-user-on-linux/
# https://medium.com/@dorukgezici/how-to-setup-python-flask-app-on-shared-hosting-without-root-access-e40f95ccc819
# Also add a search path to pin selected point onto map
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

@app.route('/map', methods = ["POST", "GET"])
def map():
    db = get_db()
    c = db.cursor()
    bed_post = []
    price_post = []
    if request.method == 'GET':
        c.execute("SELECT location, price, bedroom_num, bath_num, url, lat, lng from room")
    else: # POST
        bed_post = request.form.getlist('bed_post')
        price_post = request.form.getlist('price_post')
        # print(bed_post)
        # print(price_post)
        cmd = "SELECT location, price, bedroom_num, bath_num, url, lat, lng from room WHERE "
        for i in bed_post:
            cmd = cmd + "bedroom_num = " + str(i) + " OR "
        for i in price_post:
            # TODO: change price to unit_price!
            cmd = cmd + "(price >= " + i + " AND price <= " + i + "+200) OR "
        cmd = cmd[:-3]
        c.execute(cmd)

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
        
    rent = process_rent(rent)
    unit_rent = np.array(rent) / np.array(bed)
    length = len(address)
    return render_template('map.html', address = address, lat = lat, lng = lng, rent=rent, unit_rent = unit_rent, bed=bed, bath=bath, url=url, length=length, bed_post=bed_post, price_post=price_post)
    
def process_rent(rent):
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
        # year = request.form.get('year')
        location = request.form.get('direction')
        gym = request.form.get('gym')
        cook = request.form.get('cook')
        commute = request.form.get('commute')
        study = request.form.get('study')
        # pet = request.form.get('pet')
        # result should be a list of (lat, lng)
        result = give_result_lat_lng(location, gym, cook, commute, study)
        session['recommend_result'] = result.tolist()
        return redirect(url_for('result'))
        # return redirect(url_for('result'))
        
def give_result_lat_lng(location, gym, eat, car, study):
    db = get_db()
    c = db.cursor()
    result=score(location,gym,eat,car,study)
    lat_lng=[]
    for i in range(20):
        c.execute("SELECT lat,lng FROM room WHERE location=?",[result[i][0]])
        answer=c.fetchone()
        lat_lng.append([answer[0],answer[1]])
    lat_lng=np.array(lat_lng)
    return lat_lng

def get_home_dict():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT location,rscore,gymscore,marketscore,libraryscore,north,out  FROM room")
    h=c.fetchall()
    c.execute("SELECT COUNT(*) FROM room")
    count=c.fetchone()
    count=count[0]
    home_dict=[]
    for i in range(count):
        home_dict.append([h[i][0],h[i][1],h[i][2],h[i][3],h[i][4],h[i][5],h[i][6]])
    home_dict=np.array(home_dict)
    return home_dict

def score(location,gym,eat,car,study):
    #rscore=list[0]
    #rscore=srestaurantrate*srscore+orestaurantrate*orscore
    home_dict=get_home_dict()
    restaurantrate=0.3
    gymrate=0.1
    marketrate=0.3
    libraryrate=0.2
    nsrate=1.0
    """if ('year' == 'fresh'):
        srestaurantrate = 0.8
        orestaurantrate = 0.2
    else:
        srestaurantrate = 0.1
        orestaurantrate = 0.9"""

    ###For location,question2:
    # north==1,south==0



    ###For gym, question3:
    if (gym == 1.0):
        gymrate = 0.1
    elif (gym == 2.0):
        gymrate = 0.15
    elif (gym == 3.0):
        gymrate = 0.25
    else:
        gymrate = 0.3

    ###For question4:
    # cook==1
    if (eat == 1.0):
        restaurantrate = 0.25
        marketrate = 0.7

    ###For question5##  :
    # car==1

    if (car == 0.0):
        newhome_dict=[]
        for i in range(home_dict.shape[0]):
            if (home_dict[i][6].astype(float) == 0):  ##This means that the house is not on campus:
                newhome_dict.append(home_dict[i])
        home_dict = np.array(newhome_dict)

    ###For question6
    #library=0
    if (study == 0.0):
        libraryrate = 0.3
    #print(home_dict)
    #rscore=srestaurantrate*srscore+orestaurantrate*orscore
    result=[]
    for i in range(home_dict.shape[0]):
        # north==1,south==0
        if (location == 1) and (home_dict[i][5].astype(float) == 0):
            ###This means if the house is in the north, house is equal to zero
            nsrate = 0.66666666
        elif (location == 0) and (home_dict[i][5].astype(float) == 1):
            ###This means if the house is in the south house is equal to one
            nsrate = 0.66666666
        restaurantscore=home_dict[i][1].astype(float)
        gymscore=home_dict[i][2].astype(float)
        marketscore=home_dict[i][3].astype(float)
        libraryscore=home_dict[i][4].astype(float)
        finalscore=(nsrate*(restaurantrate*restaurantscore+gymrate*gymscore+marketrate*marketscore+libraryrate*libraryscore))/(restaurantrate+gymrate+marketrate+libraryrate)
        result.append([home_dict[i][0],finalscore])
    result=np.array(result)
    #print(result)
    result = result[result[:,-1].argsort()]
    #print(result)
    return result

# def recommend_result(year, direction, gym, cook, commute, study):
#     # get all lat/lngs
#     db = get_db()
#     c = db.cursor()
#     c.execute("SELECT lat, lng from room")
#     latlng = c.fetchall()
#
#     crce = np.array([40.1046767,-88.2239516])
#     arc = np.array([40.1015275,-88.2385425])
#     green_st = np.array([40.1101803,-88.2308469])
#     # or nearby search https://developers.google.com/places/web-service/search#PlaceSearchRequests
#     library = np.array([])
#     # return 20( or: inside knn() define a max value, return samples less than max) samples according to choice

    
@app.route('/result', methods=['POST', 'GET'])
def result():
    locations = session['recommend_result']
    db = get_db()
    c = db.cursor()
    bed_post = []
    price_post = []
    whole_profile = []
    # if request.method == 'GET':
    for latLng in locations:
        c.execute("SELECT location, price, bedroom_num, bath_num, url, lat, \
                    lng from room WHERE lat = ? AND lng = ?", [latLng[0], latLng[1]])
        
        whole_profile.append(c.fetchone())

    if request.method == 'POST':
        bed_post = request.form.getlist('bed_post')
        price_post = request.form.getlist('price_post')
        for each_profile in whole_profile:
            if not each_profile[2] in bed_post or not each_profile[1] in price_post:
                whole_profile.remove(each_profile)
    
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
    return render_template('result.html', address=address, lat=lat, lng=lng, rent=rent, unit_rent=unit_rent, bed=bed, bath=bath, url=url, length=length)

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
    
    user_likes = []
    if c_fetchone[0] == 0 or c_fetchone == None:
        location=''
        likeornot = 0
        db.commit()
    else:
        c.execute('SELECT location, likeornot  FROM likes WHERE NetID = ?', [netid])
        user_likes=c.fetchall()
        location=user_likes[0][0]
        likeornot=user_likes[0][1]
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
    c.execute('SELECT roomImage.img0, roomImage.img1, roomImage.img2, roomImage.img3, roomImage.img4 FROM room, roomImage WHERE room.location = ? AND room.id = roomImage.id', ([location]))
    house_images = c.fetchone()
    c.execute('SELECT electricity, water, internet, furnished, tv, dishwasher, \
                price, bedroom_num, bath_num, url FROM room WHERE location = ?', [location])
    house_profile = c.fetchone()
    # print(house_profile)
    electricity, water, internet, furnished, tv, dishwasher, price, bedroom_num, bath_num = process_house_profile(house_profile)
    # print(house_images)
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
        return render_template('house_profile.html', electricity=electricity, water=water, internet=internet, furnished=furnished, tv=tv, dishwasher=dishwasher, price=price, bedroom_num=bedroom_num, bath_num=bath_num, house_images=house_images, location=location,likeornot=likeornot,word=word,allcomments=allcomments,avgscore=avgscore,count=count)
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
        return render_template('house_profile.html', electricity=electricity, water=water, internet=internet, furnished=furnished, tv=tv, dishwasher=dishwasher, price=price, bedroom_num=bedroom_num, bath_num=bath_num, house_images=house_images, location=location,allcomments=allcomments,avgscore=avgscore,count=count)

def process_house_profile(house_profile):
    electricity = "Yes" if house_profile[0] == 1 else "No"
    water = "Yes" if house_profile[1] == 1 else "No"
    internet = "Yes" if house_profile[2] == 1 else "No"
    furnished = "Yes" if house_profile[3] == 1 else "No"
    tv = "Yes" if house_profile[4] == 1 else "No"
    dishwasher = "Yes" if house_profile[5] == 1 else "No"
    price = house_profile[6]
    bedroom_num = house_profile[7]
    bath_num = house_profile[8]
    return electricity, water, internet, furnished, tv, dishwasher, price, bedroom_num, bath_num
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
    c = db.cursor()
    with app.open_resource('TenantUnionPlus.sql', mode='r') as f:
        c.executescript(f.read())

    init_facilities('library')
    init_facilities('restaurant')
    init_facilities('supermarket')
    init_facilities('gym')
    
    c.execute("SELECT * FROM library")
    library=c.fetchall()
    c.execute("SELECT * FROM restaurant")
    restaurant=c.fetchall()
    c.execute("SELECT * FROM gym")
    gym=c.fetchall()
    c.execute("SELECT * FROM supermarket")
    market=c.fetchall()
    
    images, url, address, bed, bath, rent, electricity, water, internet, furnished, tv, dishwasher = get_house_info()
    print("Total", len(address), "of apartments")
    lat, lng = init_house_lat_lng(address)
    
    for i, URL in enumerate(address):
        rscore=999999.0
        gymscore=999999.0
        marketscore=999999.0
        libraryscore=999999.0
        north=0.0
        out=0.0
        if lat[i]>41.9398312:
            north=1

        if lat[i]>40.116364 or lng[i]<-88.233661 or lat[i]<40.098189 or lng[i]>-88.219099:
            out=1
        c.execute("SELECT COUNT(*) FROM restaurant")
        count=c.fetchone()
        count=count[0]
        for j in range(count):
            new_len=(lat[i]-restaurant[j][1])**2+(lng[i]-restaurant[j][2])**2
            if(rscore>new_len):
                rscore=new_len
        c.execute("SELECT COUNT(*) FROM gym")
        count=c.fetchone()
        count=count[0]
        for j in range(count):
            new_len=(lat[i]-gym[j][1])**2+(lng[i]-gym[j][2])**2
            if(gymscore>new_len):
                gymscore=new_len
        c.execute("SELECT COUNT(*) FROM supermarket")
        count=c.fetchone()
        count=count[0]
        for j in range(count):
            new_len=(lat[i]-market[j][1])**2+(lng[i]-market[j][2])**2
            if(marketscore>new_len):
                marketscore=new_len
        c.execute("SELECT COUNT(*) FROM library")
        count=c.fetchone()
        count=count[0]
        for j in range(count):
            new_len=(float(lat[i])-library[j][1])**2+(lng[i]-library[j][2])**2
            if(libraryscore>new_len):
                libraryscore=new_len

        c.execute("INSERT INTO room(id, electricity, water, internet, furnished, tv, dishwasher, \
                    location, price, bedroom_num, bath_num, url, lat, lng, north, out, rscore, gymscore, marketscore, libraryscore) \
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                    [i, electricity[i], water[i], \
                        internet[i], furnished[i], tv[i], dishwasher[i], address[i], \
                        rent[i], bed[i], bath[i], url[i], lat[i], lng[i], \
                        north, out, rscore, gymscore, marketscore, libraryscore])
        c.execute("INSERT INTO roomImage(id, img0, img1, img2, img3, img4) VALUES (?, ?, ?, ?, ?, ?)", \
                    [i, images[i][0], images[i][1], images[i][2], images[i][3], \
                        images[i][4]])
    db.commit()

def init_facilities(facility):
    db = get_db()
    c = db.cursor()
    name, lat, lng = init_facilities_lat_lng(facility)
    for i, _ in enumerate(name):
        c.execute("INSERT INTO " + facility + "(building_name, lat, lng) VALUES (?, ?, ?)", \
                [name[i], lat[i], lng[i]])
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

def init_facilities_lat_lng(facility):
    union_latlng = {"lat": 40.1094592, "lng": -88.2283148}
    google_places = GooglePlaces(client_secret["map"]["api1"])
    query_result = google_places.nearby_search(radius=5000, lat_lng = union_latlng, type=facility)
    name = []
    lat = []
    lng = []
    i = 0
    for place in query_result.places:
        i += 1
        name.append(place.name)
        lat.append(float(place.geo_location[u'lat']))
        lng.append(float(place.geo_location[u'lng']))
    print("Number of", facility, ":", i)
    return name, lat, lng
    # https://github.com/slimkrazy/python-google-places

def update_house():
    db = get_db()
    c = db.cursor()
    images, url, address, bed, bath, rent, electricity, water, internet, furnished, tv, dishwasher = get_house_info()
    lat, lng = init_house_lat_lng(address)
    c.execute("SELECT * FROM library")
    library=c.fetchall()
    c.execute("SELECT * FROM restaurant")
    restaurant=c.fetchall()
    c.execute("SELECT * FROM gym")
    gym=c.fetchall()
    c.execute("SELECT * FROM supermarket")
    market=c.fetchall()
    
    ''' TRIGGER? '''
    # check house information deletion
    c.execute("SELECT location, price, bedroom_num, bath_num, url, id, electricity, water, internet, furnished, tv, dishwasher from room")
    whole_profile = c.fetchall()
    for each_profile in whole_profile:
        ''' TODO: may need to update 'each_profile[5]' when adding more attribute! '''
        URL_db = each_profile[4]
        if URL_db in url:
            pass
        else:   # house information was deleted from TenantUnion
            c.execute("DELETE FROM room WHERE url = ?", [URL_db])

    # check house information update
    for i, URL in enumerate(url):
        c.execute("SELECT * FROM room WHERE url = ?", [URL])
        house_profile = c.fetchone()
        if house_profile == None or house_profile == 0: # new house added
            c.execute("SELECT id FROM room ORDER BY id DESC") # Get max index
            maxIdx = c.fetchone()[0] + 1
            for i, URL in enumerate(address):
                rscore=999999.0
                gymscore=999999.0
                marketscore=999999.0
                libraryscore=999999.0
                north=0.0
                out=0.0
                if lat[i]>41.9398312:
                    north=1

                if lat[i]>40.116364 or lng[i]<-88.233661 or lat[i]<40.098189 or lng[i]>-88.219099:
                    out=1
                c.execute("SELECT COUNT(*) FROM restaurant")
                count=c.fetchone()
                count=count[0]
                for j in range(count):
                    new_len=(lat[i]-restaurant[j][1])**2+(lng[i]-restaurant[j][2])**2
                    if(rscore>new_len):
                        rscore=new_len
                c.execute("SELECT COUNT(*) FROM gym")
                count=c.fetchone()
                count=count[0]
                for j in range(count):
                    new_len=(lat[i]-gym[j][1])**2+(lng[i]-gym[j][2])**2
                    if(gymscore>new_len):
                        gymscore=new_len
                c.execute("SELECT COUNT(*) FROM supermarket")
                count=c.fetchone()
                count=count[0]
                for j in range(count):
                    new_len=(lat[i]-market[j][1])**2+(lng[i]-market[j][2])**2
                    if(marketscore>new_len):
                        marketscore=new_len
                c.execute("SELECT COUNT(*) FROM library")
                count=c.fetchone()
                count=count[0]
                for j in range(count):
                    new_len=(float(lat[i])-library[j][1])**2+(lng[i]-library[j][2])**2
                    if(libraryscore>new_len):
                        libraryscore=new_len

                c.execute("INSERT INTO room(id, electricity, water, internet, furnished, tv, dishwasher, \
                            location, price, bedroom_num, bath_num, url, lat, lng, north, out, rscore, gymscore, marketscore, libraryscore) \
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                            [i+maxIdx, electricity[i], water[i], \
                                internet[i], furnished[i], tv[i], dishwasher[i], address[i], \
                                rent[i], bed[i], bath[i], url[i], lat[i], lng[i], \
                                north, out, rscore, gymscore, marketscore, libraryscore])
                c.execute("INSERT INTO roomImage(id, img0, img1, img2, img3, img4) VALUES (?, ?, ?, ?, ?, ?)", \
                            [i+maxIdx, images[i][0], images[i][1], images[i][2], images[i][3], \
                                images[i][4]])

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
