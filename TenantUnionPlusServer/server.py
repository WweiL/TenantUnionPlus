
import os
import requests
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
# from TenantUnionPlus import *

     
app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'TenantUnionPlus.db'),
    SECRET_KEY='wBwhfdLNVp0pCQqL5lVIgmXf',
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
SCOPES = ['profile']#, 'email']
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

    user_email = people_document['emails'][0][u'value'] # get user email
    user_email_splitted = user_email.split('@')
    user_netid = user_email_splitted[0]
    user_email_suffix = user_email_splitted[1]
    session['netid'] = user_netid
    if user_email_suffix != "illinois.edu":
        flash("You should use a illinois email to log in")
        return redirect(url_for('logout'))
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    session['credentials'] = credentials_to_dict(credentials)
    session['logged_in'] = True
    
    # DATABASE
    db = get_db()
    c = db.cursor()
    c.execute('SELECT count(*) FROM student WHERE NetID = (?)', [user_netid])
    if c.fetchone() == 0:
        c.execute('INSERT INTO student (NetID) values (?)', [user_netid])
    db.commit()

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('credentials', None)
    session.pop('netid', None)
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
    if session.get('logged_in'):
        return render_template('navbarLoggedIn.html')
    else:
        return render_template('navbarNotLoggedIn.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    return render_template('/pages/question/question.html')

@app.route('/result/')
def result():
    # if request.form.getlist('')....
    return 'result'

@app.route('/user/<netid>')
def profile(netid):
    if not session.get('logged_in'):
        flash("You need to log in to see your profile")
        abort(401)
    db = get_db()
    # # TODO:change this to suit our project
    # db.execute('insert into entries (title, text) values (?, ?)',
    #              [request.form['title'], request.form['text']])
    c = db.cursor()
    c.execute('SELECT * FROM student WHERE NetID = (?)', [netid])
    user_profile = c.fetchone()
    db.commit()

    return render_template('user_profile.html', netid=netid)
    

@app.route('/house/info/<house_id>')
def houseInfo():
    return 'houseInfo'


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
    with app.open_resource('student.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
