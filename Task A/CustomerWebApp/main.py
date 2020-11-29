import os, requests, string, random
from random import randint
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.contrib.fixers import ProxyFix
from flask_dance.contrib.google import make_google_blueprint, google
from raven.contrib.flask import Sentry
from requests_toolbelt.adapters import appengine

# <--------------------------------------------------->
#                   calendar import
import sys, json, flask, flask_socketio, httplib2
from flask import Response, request
from apiclient import discovery
from oauth2client import client
from googleapiclient import sample_tools
from rfc3339 import rfc3339
from dateutil import parser

"""
A Flask web app served as a front end for customers.

The web app uses Flask as the app framework, with Python being the primary coding platform and HTML/CSS serves to build web templates.

The app functions and features include:
    Signing up, logging in, and logging out
    Google account support
    Browsing, searching, and booking cars
    Adding booking event to Google Calendar
    Viewing and cancelling bookings
    A clean, minimal UI
    RESTful API
"""

app = Flask(__name__, static_url_path='/static', static_folder='/static')

# Init App
appengine.monkeypatch()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.wsgi_app = ProxyFix(app.wsgi_app)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = os.environ.get("OAUTHLIB_INSECURE_TRANSPORT")
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = os.environ.get("OAUTHLIB_RELAX_TOKEN_SCOPE")

# Config Google OAuth

app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
google_bp = make_google_blueprint(scope=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'])
app.register_blueprint(google_bp, url_prefix="/login")

# Config MySQL
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
app.config['MYSQL_UNIX_SOCKET'] = os.environ.get("MYSQL_UNIX_SOCKET")
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
app.config['MYSQL_CURSORCLASS'] = os.environ.get("MYSQL_CURSORCLASS")

mysql = MySQL(app)

@app.route('/')
def index():
    """
    Render the home page.

    The fuction renders the file home.html in /templates.

    Returns:
        render_template('home.html'): Renders the file home.html in /templates.
    """

    return render_template('home.html')

def is_logged_in(f):
    """
    A decorator that check if the user is logged in.

    The function checks if the current session is logged in and proceeds if true. Otherwise, the function redirect to the login page with an error message. 
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized. Please login.', 'danger')
            return redirect(url_for('login'))
    return wrap

# Car Menu
@app.route('/car_menu')
@is_logged_in
def get_cates_1():
    """
    Render the car menu page.

    The function establishes a connection to the database and get the car categories. Then, the function render car_menu.html in /templates with the given querry results or an error message.

    Returns:
        render_template('car_menu.html', cates=cates): Render car_menu.html in /templates and pass the querry array to the template.
        render_template('car_menu.html', msg=msg): Render car_menu.html in /templates and pass an error message to the template.
    """

    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM cars WHERE make='category'")

    cates = cur.fetchall()

    if result > 0:
        return render_template('car_menu.html', cates=cates)
    else:
        msg = 'No categories found.'
        return render_template('car_menu.html', msg=msg)
    # Close connection
    cur.close()

# View Booked Car History
# @app.route('/history')
# @is_logged_in
# def view_history():
#     # Create cursor
#     cur = mysql.connection.cursor()

#     # Get articles
#     cur.execute("SELECT * FROM bookings WHERE userId=%s", [session['id']])
#     new_data = cur.fetchall()
#     booked_carIds=[]
#     for new_row in new_data:
#         booked_carIds.append(new_row['carId'])

#     cars=[]
#     for x in range(len(booked_carIds)):
#         cur.execute("SELECT * FROM cars WHERE carStatus='Booked' AND id=%s", [booked_carIds[x]])
#         result=cur.fetchone()
#         cars.append(result)

#     if len(cars) > 0:
#         return render_template('history.html', cars=cars)
#     else:
#         msg = 'No cars found.'
#         return render_template('history.html', msg=msg)
#     # Close connection
#     cur.close()

#Display Cars Based On Category
@app.route('/car_menu/<string:body>/')
def get_cars_1(body):
    """
    Render the car selection page based on the selected car category.

    The function establishes a connection to the database and get the cars based on the given category. Then, the function render cars.html in /templates with the given querry results or an error message.

    Arguments:
        string body: the name of the category to be used to querry the database.

    Returns:
        render_template('cars.html', cars=cars): Render cars.html in /templates and pass the querry array to the template.
        render_template('cars.html', msg=msg): Render cars.html in /templates and pass an error message to the template.
    """

    # Create cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM cars WHERE make!='category' AND bodyType = %s", [body])

    cars = cur.fetchall()

    if len(cars) > 0:
        return render_template('cars.html', cars=cars)
    else:
        msg = 'No cars found.'
        return render_template('cars.html', msg=msg)
    # Close connection
    cur.close()

# Register Form Class
class RegisterForm(Form):
    """
    This class contains variables that serves as fields in the user registration form.
    """

    username = StringField('''<p class="label-p">Username</p>''', [validators.Length(min=4, max=30)])
    firstname = StringField('''<p class="label-p">First Name</p>''', [validators.Length(min=1, max=30)])
    lastname = StringField('''<p class="label-p">Last Name</p>''', [validators.Length(min=1, max=30)])
    gmail = StringField('''<p class="label-p">Email</p>''', [validators.Length(min=14, max=50)])
    # userType = StringField('''<p class="label-p">User Type</p>''', [validators.Length(min=4, max=8)]) #do we need this for customers?
    # macAd = StringField('macAd', [validators.Length(min=4, max=17)])
    password = PasswordField('''<p class="label-p">Password</p>''', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('''<p class="label-p">Confirm Password</p>''')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Render the user registration form and process the input.

    The function renders register.html in /templates, which has a user registration form. It takes the user's inputs from the form and validate them. If the validation is sucessful, the function process the inputs, establish a connection with the database, and create a new user entry on the databse. The function redirect to the login page if sucessful and back to the register page if not.

    Returns:
        render_template('register.html', form=form): Render register.html in /templates with the register form.
        redirect(url_for('login')): Redirect to the login page.
        redirect(url_for('register')): Redirect to the register page.
    """

    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # Note: id of user is a combined string of username and randomly generated 10 int digits
        id = form.username.data+''.join(["{}".format(randint(0, 9)) for num in range(0, 10)])
        username = form.username.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        gmail = form.gmail.data
        userType = "Customer" #form.userType.data
        macAd = ""
        salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        passSalt = form.password.data+salt
        pwd = sha256_crypt.encrypt(str(passSalt))

        # Create cursor
        cur = mysql.connection.cursor()

        # Check username duplicate
        cur.execute('SELECT * FROM users')
        username_array = cur.fetchall()
        repeat = False
        if username_array > 0:
            for row in username_array:
                if username==row['username']:
                    repeat = True
                    flash('Failed to register. Username already existed.')
                    break

        if repeat == False:
            # Execute query
            cur.execute("INSERT INTO users(id, username, firstname, lastname, pwd, salt, gmail, userType, macAd) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, username, firstname, lastname, pwd, salt, gmail, userType, macAd))

            # Commit to DB
            mysql.connection.commit()

            flash('You are now registered and can log in.', 'success')

        # Close connection
        cur.close()

        if repeat == False:
            return redirect(url_for('login'))
        else:
            return redirect(url_for('register'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Render the user login form and process the input.

    The function renders login.html in /templates, which has a user login form. It process the user's inputs, establish a connection with the database, and compare the inputs with every user entry on the database. The function redirect to the My Bookings page if there's a match on the database and back to the login page if not.

    Returns:
        render_template('login.html'): Render login.html in /templates.
        redirect(url_for('dashboard')): Redirect to the My Bookings page, which is dashbard in the codes.
        render_template('login.html', error=error): Render login.html in /templates and pass an error message.
    """

    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            id = data['id']
            password = data['pwd']
            password_target = password_candidate+data['salt']

            # Compare Passwords
            if sha256_crypt.verify(password_target, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['id'] = id
                session['login_type'] = "normal"

                #flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

        # Close connection
        cur.close()
    return render_template('login.html')

# User Login Google
@app.route('/login_google', methods=['GET', 'POST'])
def login_google():
    """
    Let the user log in using a Google account.

    The function redirects to the Google login page where the user logs in with their Google account. The function takes the user's information and compare them to every user entry on the databse. If there's no match, a new user entry is added to the database. If there's a match, the function establish a logged-in session in the app. The function redirects to the My Bookings page afterward.

    Returns:
        redirect(url_for("google.login")): Redirect to the Google login page.
        redirect(url_for('dashboard')): Redirect to the My Bookings page, which is dashbard in the codes.
    """

    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    if resp.ok and resp.text:
        name = resp.json()["name"]
        email = resp.json()["email"]
        username = resp.json()["given_name"]
        gg_id = resp.json()["id"]
        # new id is generated by a combination of username and randomly generated 10 digits
        id = username+''.join(["{}".format(randint(0, 9)) for num in range(0, 10)])
        print(resp.json())
        
        # Create cursor
        cur = mysql.connection.cursor()
        # Get user by email
        result = cur.execute("SELECT * FROM users WHERE gmail=%s AND gg_id =%s", [email, gg_id])
        if result>0:
            session['logged_in'] = True
            session['username'] = username
            cur.execute("SELECT id FROM users WHERE gmail=%s AND gg_id =%s", [email, gg_id])
            data_id = cur.fetchone()
            new_id = data_id['id']
            session['id'] = new_id
            session['login_type'] = "google"
            
            #flash('You are now logged in via Google','success')
            return redirect(url_for('dashboard'))
        else:
            # Execute Query
            cur.execute("INSERT INTO users(id, username, firstname, lastname, pwd, salt, gmail, userType, macAd, gg_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, username, name, "", "", "", email, "", "",gg_id))
            # Commit to DB
            mysql.connection.commit()
            # Close connection
            cur.close()

            session['logged_in'] = True
            session['username'] = username
            session['id'] = id
            session['login_type'] = "google"
            flash('Successfully registered via Google.','success')
            return redirect(url_for('dashboard'))
        # Close connection
        cur.close()

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    """
    Log the user out of the app.

    The function clear the session, effectively log the user out of the app. The user is redirected to the login page.

    Returns:
        redirect(url_for('login')): redirect to the login page.
    """

    session.clear()
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    """
    Display the user's booking details.

    The function establishes a connection to the database, gets all bookings from the user, get all cars from the bookings, and passes the querries to the dashboard.html template. The function returns a message if no bookings are found.

    Returns:
        render_template('dashboard.html', bookings=bookings, cars=cars): render dashboard.html from /templates, pass querry arrays to the rendered template.
        return render_template('dashboard.html', msg=msg): render dashboard.html from /templates, pass a message to the rendered template.
    """

    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    # Show articles only from the user logged in 
    result = cur.execute("SELECT * FROM bookings WHERE userId = %s", [session['id']])

    bookings = cur.fetchall()

    if result > 0:

        cur_cars = mysql.connection.cursor()

        cur_cars.execute("SELECT * FROM cars")

        cars = cur_cars.fetchall()

        return render_template('dashboard.html', bookings=bookings, cars=cars)
    else:
        msg = 'No bookings found.'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()
    cur_cars.close()

# Booking Form Class
class BookingForm(Form):
    """
    This class contains variables that serves as fields in the car booking form for users with Google accounts.
    """

    bookingDate = StringField('''<p class="label-p">Date</p>''', [validators.Length(max=10)])
    timeFrom = StringField('''<p class="label-p">Time</p>''', [validators.Length(max=5)])
    # timeTo = StringField('timeTo', [validators.Length(max=5)])
    nOHours = IntegerField('''<p class="label-p">Duration</p>''')
    # Added Fields for Google Calendar API
    eventName = StringField('''<p class="label-p">Event Name</p>''', [validators.Length(max=255)])
    cid = StringField('''<p class="label-p">Calendar ID</p>''', [validators.Length(max=255)])

# Booking Form Class
class BookingFormV2(Form):
    """
    This class contains variables that serves as fields in the car booking form for users without Google accounts.
    """

    bookingDate = StringField('''<p class="label-p">Date</p>''', [validators.Length(max=10)])
    timeFrom = StringField('''<p class="label-p">Time</p>''', [validators.Length(max=5)])
    # timeTo = StringField('timeTo', [validators.Length(max=5)])
    nOHours = IntegerField('''<p class="label-p">Duration</p>''')

#Begin oauth callback route
@app.route('/oauth2callback')
def oauth2callback():
    """
    Let Google verify the app and let the current Google user access Google Calendar.

    This function lets Google verify the app through the client_secrets.json granted by Google. If verification is successful, the user is redirected to a confirmation page to allow the app to make modification to the user's Google Calendar. Afterward, the user is redirected to the car menu page to continue booking.

    Returns:
        flask.redirect(auth_uri): redirect to a confirmation page where the user grant the app permissions to change the user's Google Calendar.
        flask.redirect(flask.url_for('get_cates_1')): redirect to the car menu page.
    """

    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events',
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('get_cates_1')) #get_cars_1

# Gets the calendar names and their corresponding ID's
def getCalendars():
    """
    Get the calendar names and their corresponding IDs.

    The function access the user's Google calendar and get the names and IDs of all the different calendars the user has.

    Returns:
        array calendars: an array containing the the names and IDs of the calendars in the user's Google Calendar.
    """

    calendars = []
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except credError:
        print("did not assign credentials")
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        calendars.append({"name": calendar_list_entry['summary'], "id": calendar_list_entry['id']})
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    return calendars

#Function to add event into calendar selected
def oauth(name, cid, sTime, eTime):
    """
    Add an event to Google Calendar.

    Arguments:
        name: name of the Google Calendar event.
        cid: Google Calendar id.
        sTime: the starting time of the event.
        eTime: the ending time of the event.

    Returns:
        new_event['id']: return the event id.
    """

    print(sTime)
    print(eTime)
    print(name)
    print(cid)
    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except credError:
        print("did not assign credentials")
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    eventName = ""
    event = {
        'summary': name,
        'start': {
        'dateTime': sTime,
        },
        'end': {
        'dateTime': eTime,
        },
        # 'iCalUID': 'originalUID',
    }
    new_event = service.events().insert(calendarId=cid, body=event).execute()
    # new_event = service.events().insert(calendarId='primary', body=event).execute()
    # new_event = service.events().import_(calendarId=cid, body=event).execute()
    print("Succesfully Imported Event")
    return new_event['id']
    # return flask.redirect(flask.url_for('calendar'))

#Function to delete event from calendar selected
def oauth_1(cid, eventId):
    """
    Delete event from Google Calendar.

    Arguments:
        cid: Google Calendar id.
        eventId: the id of the Google Calendar event.
    """

    try:
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    except credError:
        print("did not assign credentials")
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    service.events().delete(calendarId=cid, eventId=eventId).execute()
    flash("Your booking event is removed from Google Calendar.")

# Book A Car
@app.route('/add_booking', methods=['GET', 'POST'])
@is_logged_in
def make_booking():
    """
    A function to book a car.

    The function gets the id from the url, connects to the database, and gets the car with that id. The function checks if the user is a Google user and gets the appropriate booking form. The function validates and process the inputs from the form. It then adds a new Google Calendar events if applicable. A new database entry in the bookings table is added.

    Returns:
        return render_template('booking.html', calendars=calendars, form=form, car=car): Render booking.html from /templates, which is the car booking form. Pass Google cClendar details, form, and car details to the template.
        return render_template('booking.html', form=form, car=car): Render booking.html from /templates, which is the car booking form. Pass the form and car details to the template.
        return redirect(url_for('dashboard')): redirect to My Booking page when booking is sucessful.
    """

    id=request.args.get('id')

    #get the car
    cur_car = mysql.connection.cursor()
    cur_car.execute("SELECT * FROM cars WHERE id=%s", [id])
    car = cur_car.fetchone()
    cur_car.close()

    if session['login_type'] == 'google':
        if 'credentials' not in flask.session:
            return flask.redirect(flask.url_for('oauth2callback'))
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
        if credentials.access_token_expired:
            return flask.redirect(flask.url_for('oauth2callback'))
        calendars=getCalendars()

    if session['login_type']=='google':
        form = BookingForm(request.form)
    else: form = BookingFormV2(request.form)
    if request.method == 'POST' and form.validate():
        bookingDate = form.bookingDate.data
        timeFrom = form.timeFrom.data
        # timeTo = form.timeTo.data
        nOHours = form.nOHours.data
        time_var = int(timeFrom[0:2]) + nOHours
        timeTo = str(time_var)+":"+timeFrom[3:5]
        userId = session['id']
        id_1 = 0
        carId = id

        # Sample time inputs: 2017-09-20 15:00:00
        sTime_1 = bookingDate + " " + timeFrom + ":00"
        eTime_1 = bookingDate + " " + timeTo + ":00"

        # Add Customer Booking Time Event to Google Calendar
        if session['login_type']=="google":
            name = form.eventName.data
        sTime = parser.parse(sTime_1)
        eTime = parser.parse(eTime_1)
        if session['login_type']=="google":
            cid = form.cid.data
        else: cid = ""

        sConverted = rfc3339(sTime)
        eConverted = rfc3339(eTime)

        # Convert time again to UTC +7 (Bangkok, Hanoi, Jakarta Timezone)
        sC = str(sConverted).split("+")
        eC = str(eConverted).split("+")

        final_sTime = sC[0]+"+07:00"
        final_eTime = eC[0]+"+07:00"
        # reconvert_sTime = str(sConverted)[0:20]+"07:00"
        # reconvert_eTime = str(eConverted)[0:20]+"07:00"

        if session['login_type'] == "google":
            event_id = oauth(name, cid, final_sTime, final_eTime)
        else: event_id = ""

        # Create Cursor
        cur = mysql.connection.cursor()

        # Check id duplicate
        cur.execute("SELECT id FROM bookings")
        id_array = cur.fetchall()
        temp_array=[]
        if id_array > 0:
            for res_id in id_array:
                temp_array.append(int(res_id['id']))
            # id is auto-incremented
            if len(temp_array)>0:
                id_1 = max(temp_array)+1
            else: id_1 = 1
        
        # Execute
        cur.execute("INSERT INTO bookings(id, cid, eid, userId, carId, bookingDate, timeFrom, nOHours) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",(str(id_1), str(cid), str(event_id), userId, carId, bookingDate, timeFrom, nOHours))

        # Update carStatus
        cur.execute("UPDATE cars SET carStatus = 'Booked' WHERE id = %s", [id])

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Car booked successfully.', 'success')

        return redirect(url_for('dashboard'))

    if session['login_type']=='google':
        return render_template('booking.html', calendars=calendars, form=form, car=car)
    else: return render_template('booking.html', form=form, car=car)

# Delete Article
@app.route('/cancel_booking/<string:id>', methods=['POST'])
@is_logged_in
def cancel_booking(id):
    """
    Cancel a booking.

    The function takes the given id, connect to the database, and deletes the booking with that id. The function also delete the Google Calendar event if the user is a Google user.

    Arguments:
        string id: the id of the booking.

    Returns:
        redirect(url_for('dashboard')): redirect back to the My Booking page (dashboard in codes)
    """

    # id=request.args.get('booking_id')
    car_id=request.args.get('car_id')

    # Create cursor
    cur = mysql.connection.cursor()

    # Get cid (calendar_id), eid (event_id) from db and delete event from gg calendar

    if session['login_type'] == "google":
        if 'credentials' not in flask.session:
            return flask.redirect(flask.url_for('oauth2callback'))
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
        if credentials.access_token_expired:
            return flask.redirect(flask.url_for('oauth2callback'))
    
        cur.execute("SELECT cid, eid FROM bookings WHERE id = %s", [id])
        res = cur.fetchone()
        cid = res['cid']
        eid = res['eid']
        oauth_1(cid, eid)

    # Execute
    cur.execute("DELETE FROM bookings WHERE id = %s", [id])

    # Update the booked car status to be available for booking
    cur.execute("UPDATE cars SET carStatus = 'Available' WHERE id = %s", [car_id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Booking cancelled successfully.', 'success')

    return redirect(url_for('dashboard'))
    # return render_template('dashboard.html')

# Search Car Form Class
class SearchForm(Form):
    """
    This class contains variables that serves as fields in the search form.
    """

    id = StringField('''<p class="label-p">Car ID</p>''', [validators.Length(max=250)])
    carCode = StringField('''<p class="label-p">Car Code</p>''', [validators.Length(max=250)])
    make = StringField('''<p class="label-p">Car Brand</p>''', [validators.Length(max=250)])
    bodyType = StringField('''<p class="label-p">Car Type</p>''', [validators.Length(max=250)])
    colour = StringField('''<p class="label-p">Colour</p>''', [validators.Length(max=250)])
    seats = StringField('''<p class="label-p">Seat Count</p>''', [validators.Length(max=250)])
    carLocation = StringField('''<p class="label-p">Location</p>''', [validators.Length(max=250)])
    costPerHour = StringField('''<p class="label-p">Cost</p>''', [validators.Length(max=250)])
    carStatus = StringField('''<p class="label-p">Status</p>''', [validators.Length(max=250)])

# Search Results
def search_result(final_entries, search_check):
    """
    Render the search results.

    The fuction renders the file search_result.html in /templates, passing array final_entries containing search results into the template.

    Arguments:
        aarray final_entries: an array containing search results.

    Returns:
        render_template('search_result.html', final_entries=final_entries): Renders the search_result home.html in /templates, passing array final_entries.
    """

    return render_template('search_result.html', final_entries=final_entries, search_check=search_check)

# Search A Car
@app.route('/search_car', methods=['GET', 'POST'])
@is_logged_in
def search_car():
    """
    Render the search form, process the input, and display search results.

    The function renders search.html in /templates, which has a search form. It takes the user's inputs from the form and validate them. If the validation is sucessful, the function process the inputs, establish a connection with the database, and querries all car entries on the databse that match with the inputs. The function returns a list of results if there are matches.

    Returns:
        render_template('search_form.html', form=form): Render search.html in /templates with the search form.
        return search_result(final_entries): call a function to display all querried entries
    """

    search_check = 0

    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        id = form.id.data
        carCode = form.carCode.data
        make = form.make.data
        bodyType = form.bodyType.data
        colour = form.colour.data
        if form.seats.data!="" and form.seats.data.isdigit()==True:
            seats = int(form.seats.data)
        else: seats=0
        carLocation = form.carLocation.data
        if form.costPerHour.data!="" and form.costPerHour.data.isdigit()==True:
            costPerHour = int(form.costPerHour.data)
        else: costPerHour=0
        carStatus = form.carStatus.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        All_results = []
        All_entries = []

        # if id != "" and carCode=="" and make=="" and bodyType=="" and colour=="" and seats==0 and carLocation=="" and costPerHour==0 and carStatus=="":
        if id != "":
            cur.execute("SELECT * FROM cars WHERE id LIKE %s", [id])
            result_id = cur.fetchall()
            if result_id > 0:
                for res_id in result_id:
                    All_results.append(res_id['id'])
                    All_entries.append(res_id)
        # if id=="" and carCode != "" and make=="" and bodyType=="" and colour=="" and seats==0 and carLocation=="" and costPerHour==0 and carStatus=="":
        if carCode != "":
            cur.execute("SELECT * FROM cars WHERE carCode LIKE %s", [carCode])
            result_carCode = cur.fetchall()
            if result_carCode > 0:
                for res_carCode in result_carCode:
                    All_results.append(res_carCode['id'])
                    All_entries.append(res_carCode)
        # if id=="" and carCode=="" and make != "" and bodyType=="" and colour=="" and seats==0 and carLocation=="" and costPerHour==0 and carStatus=="":
        if make != "":
            cur.execute("SELECT * FROM cars WHERE make LIKE %s", [make])
            result_make = cur.fetchall()
            if result_make > 0:
                for res_make in result_make:
                    All_results.append(res_make['id'])
                    All_entries.append(res_make)
        # if id=="" and carCode=="" and make=="" and bodyType != "" and colour=="" and seats==0 and carLocation=="" and costPerHour==0 and carStatus=="":
        if bodyType != "":
            cur.execute("SELECT * FROM cars WHERE bodyType LIKE %s AND make != 'category'", [bodyType])
            result_bodyType = cur.fetchall()
            if result_bodyType > 0:
                for res_bodyType in result_bodyType:
                    All_results.append(res_bodyType['id'])
                    All_entries.append(res_bodyType)
        # if id=="" and carCode=="" and make=="" and bodyType=="" and colour != "" and seats==0 and carLocation=="" and costPerHour==0 and carStatus=="":
        if colour != "":
            cur.execute("SELECT * FROM cars WHERE colour LIKE %s", [colour])
            result_colour = cur.fetchall()
            if result_colour > 0:
                for res_colour in result_colour:
                    All_results.append(res_colour['id'])
                    All_entries.append(res_colour)
        # if id=="" and carCode=="" and make=="" and bodyType=="" and colour=="" and seats != 0 and carLocation=="" and costPerHour==0 and carStatus=="":
        if seats != 0:
            cur.execute("SELECT * FROM cars WHERE seats LIKE %s", [seats])
            result_seats = cur.fetchall()
            if result_seats > 0:
                for res_seats in result_seats:
                    All_results.append(res_seats['id'])
                    All_entries.append(res_seats)
        # if id=="" and carCode=="" and make=="" and bodyType=="" and colour=="" and seats==0 and carLocation != "" and costPerHour==0 and carStatus=="":
        if carLocation != "":
            cur.execute("SELECT * FROM cars WHERE carLocation LIKE %s", [carLocation])
            result_carLocation = cur.fetchall()
            if result_carLocation > 0:
                for res_carLocation in result_carLocation:
                    All_results.append(res_carLocation['id'])
                    All_entries.append(res_carLocation)
        # if id=="" and carCode=="" and make=="" and bodyType=="" and colour=="" and seats==0 and carLocation=="" and costPerHour != 0 and carStatus=="":
        if costPerHour != 0:
            cur.execute("SELECT * FROM cars WHERE costPerHour LIKE %s", [costPerHour])
            result_costPerHour = cur.fetchall()
            if result_costPerHour > 0:
                for res_costPerHour in result_costPerHour:
                    All_results.append(res_costPerHour['id'])
                    All_entries.append(res_costPerHour)
        # if id=="" and carCode=="" and make=="" and bodyType=="" and colour=="" and seats==0 and carLocation=="" and costPerHour==0 and carStatus != "":
        if carStatus != "":
            cur.execute("SELECT * FROM cars WHERE carStatus LIKE %s", [carStatus])
            result_carStatus = cur.fetchall()
            if result_carStatus > 0:
                for res_carStatus in result_carStatus:
                    All_results.append(res_carStatus['id'])
                    All_entries.append(res_carStatus)

        # Remove duplicates from All_results
        final_result = []
        for item in All_results:
            if item not in final_result:
                final_result.append(item)

        final_entries = []
        for x in range(len(final_result)):
            cur.execute("SELECT * FROM cars WHERE id=%s", [final_result[x]])
            target_item = cur.fetchone()
            final_entries.append(target_item)

        #Close connection
        cur.close()

        if len(final_entries) > 0:
            
            search_check = 1

            return search_result(final_entries, search_check)
        else: flash('No cars found.')

    return render_template('search_form.html', form=form, search_check = search_check)


# --------------------------------------------------------------------------------------------------------------------

# REST API Components

# GET cars
@app.route('/api/cars')
def get_cars():
    """
    An implementation of a GET method to retrieve all entries in the cars table in the database.

    The function is called when a GET request is received with the url /api/cars. The function connects to the database, and retrieve all cars. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM cars")
        cars = cursor.fetchall()
        res = jsonify(cars)
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# GET cars BY ID
@app.route('/api/cars/<string:id>')
def get_car(id):
    """
    An implementation of a GET method to retrieve an entry by id in the cars table in the database.

    The function is called when a GET request is received with the url /api/cars/<string:id>, where id is the id of a car in the database. The function takes the id, connects to the database, and retrieve the car with that id. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM cars WHERE id=%s", [id])
        row = cursor.fetchone()
        res = jsonify(row)
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# POST cars
@app.route('/api/cars', methods=['POST'])
def add_cars():
    """
    An implementation of a POST method to create an entry in the cars table in the database.

    The function is called when a POST request is received with the url /api/cars. A json body is expected with the PUT request. The function takes the body content, connects to the database, and create a new car. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        _json = request.json
        _id = _json['id']
        _carCode = _json['carCode']
        _make = _json['make']
        _carName = _json['carName']
        _bodyType = _json['bodyType']
        _colour = _json['colour']
        _seats = _json['seats']
        _carLocation = _json['carLocation']
        _costPerHour = _json['costPerHour']
        _carStatus = _json['carStatus']
        _carImage = _json['carImage']
        
        # insert record in database
        sqlQuery = "INSERT INTO cars(id, carCode, make, carName, bodyType, colour, seats, carLocation, costPerHour, carStatus, carImage) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (_id, _carCode, _make, _carName, _bodyType, _colour, _seats, _carLocation, _costPerHour, _carStatus, _carImage,)
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        cursor.execute(sqlQuery, data)
        # conn.commit()
        mysql.connection.commit()
        res = jsonify('Car created successfully.')
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    else:
        return not_found()
    # finally:
    #     cursor.close() 
        # conn.close()

# PUT cars
@app.route('/api/cars', methods=['PUT'])
def update_cars():
    """
    An implementation of a PUT method to update an entry in the cars table in the database.

    The function is called when a PUT request is received with the url /api/cars. A json body with the proper car id is expected with the PUT request. The function takes the body content, connects to the database, and update the respective car. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        _json = request.json
        _id = _json['id']
        _carCode = _json['carCode']
        _make = _json['make']
        _carName = _json['carName']
        _bodyType = _json['bodyType']
        _colour = _json['colour']
        _seats = _json['seats']
        _carLocation = _json['carLocation']
        _costPerHour = _json['costPerHour']
        _carStatus = _json['carStatus']
        _carImage = _json['carImage']
        
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        if _id and request.method == 'PUT':
            # update record in database
            sql = "UPDATE cars SET carCode=%s, make=%s, carName=%s, bodyType=%s, colour=%s, seats=%s, carLocation=%s, costPerHour=%s, carStatus=%s, carImage=%s WHERE id=%s"
            data = (_carCode, _make, _carName, _bodyType, _colour, _seats, _carLocation, _costPerHour, _carStatus, _carImage, _id,)
            cursor.execute(sql, data)
            # conn.commit()
            mysql.connection.commit()
            res = jsonify('Car updated successfully.')
            res.status_code = 200
            return res
        else:
            return not_found()
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# DELETE car		
@app.route('/api/cars/<string:id>', methods=['DELETE'])
def delete_cars(id):
    """
    An implementation of a DELETE method to delete an entry from the cars table in the database.

    The function is called when a DELETE request is received with the url /api/cars/<string:id>, where id is the id of a car in the database. The function takes the id, connects to the database, and deletes the car with that id. A confirmation json message is returned.  

    Arguments:
        string id: the id of the car in the database.

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM cars WHERE id=%s", [id])
        # conn.commit()
        mysql.connection.commit()
        res = jsonify('Car deleted successfully.')
        res.status_code = 200
        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# GET bookings
@app.route('/api/bookings')
def get_bookings():
    """
    An implementation of a GET method to retrieve all entries in the bookings table in the database.

    The function is called when a GET request is received with the url /api/bookings. The function connects to the database, and retrieve all bookings. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()
        res = jsonify(bookings)
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# GET bookings BY ID
@app.route('/api/bookings/<string:id>')
def get_booking(id):
    """
    An implementation of a GET method to retrieve an entry by id in the bookings table in the database.

    The function is called when a GET request is received with the url /api/bookings/<string:id>, where id is the id of a booking in the database. The function takes the id, connects to the database, and retrieve the booking with that id. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM bookings WHERE id=%s", [id])
        row = cursor.fetchone()
        res = jsonify(row)
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# POST bookings
@app.route('/api/bookings', methods=['POST'])
def add_bookings():
    """
    An implementation of a POST method to create an entry in the bookings table in the database.

    The function is called when a POST request is received with the url /api/bookings. A json body is expected with the PUT request. The function takes the body content, connects to the database, and create a new booking. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        _json = request.json
        _id = _json['id']
        _cid = _json['cid']
        _eid = _json['eid']
        _userId = _json['userId']
        _carId = _json['carId']
        _bookingDate = _json['bookingDate']
        _timeFrom = _json['timeFrom']
        _nOHours = _json['nOHours']
        
        # insert record in database
        sqlQuery = "INSERT INTO bookings(id, cid, eid, userId, carId, bookingDate, timeFrom, nOHours) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        data = (_id, _cid, _eid, _userId, _carId, _bookingDate, _timeFrom, _nOHours,)
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        cursor.execute(sqlQuery, data)
        # conn.commit()
        mysql.connection.commit()
        res = jsonify('Booking created successfully.')
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    else:
        return not_found()
    # finally:
    #     cursor.close() 
        # conn.close()

# PUT bookings
@app.route('/api/bookings', methods=['PUT'])
def update_bookings():
    """
    An implementation of a PUT method to update an entry in the bookings table in the database.

    The function is called when a PUT request is received with the url /api/bookings. A json body with the proper booking id is expected with the PUT request. The function takes the body content, connects to the database, and update the respective booking. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        _json = request.json
        _id = _json['id']
        _cid = _json['cid']
        _eid = _json['eid']
        _userId = _json['userId']
        _carId = _json['carId']
        _bookingDate = _json['bookingDate']
        _timeFrom = _json['timeFrom']
        _nOHours = _json['nOHours']
        
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        if _id and request.method == 'PUT':
            # update record in database
            sql = "UPDATE bookings SET cid=%s, eid=%s, userId=%s, carId=%s, bookingDate=%s, timeFrom=%s, nOHours=%s WHERE id=%s"
            data = (_cid, _eid, _userId, _carId, _bookingDate, _timeFrom, _nOHours, _id,)
            cursor.execute(sql, data)
            # conn.commit()
            mysql.connection.commit()
            res = jsonify('Booking updated successfully.')
            res.status_code = 200
            return res
        else:
            return not_found()
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# DELETE booking		
@app.route('/api/bookings/<string:id>', methods=['DELETE'])
def delete_bookings(id):
    """
    An implementation of a DELETE method to delete an entry from the bookings table in the database.

    The function is called when a DELETE request is received with the url /api/bookings/<string:id>, where id is the id of a booking in the database. The function takes the id, connects to the database, and deletes the booking with that id. A confirmation json message is returned.  

    Arguments:
        string id: the id of the booking in the database.

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM bookings WHERE id=%s", [id])
        # conn.commit()
        mysql.connection.commit()
        res = jsonify('Booking deleted successfully.')
        res.status_code = 200
        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# GET users
@app.route('/api/users')
def get_users():
    """
    An implementation of a GET method to retrieve all entries in the users table in the database.

    The function is called when a GET request is received with the url /api/users. The function connects to the database, and retrieve all users. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        res = jsonify(users)
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# GET users BY ID
@app.route('/api/users/<string:id>')
def get_user(id):
    """
    An implementation of a GET method to retrieve an entry by id in the users table in the database.

    The function is called when a GET request is received with the url /api/users/<string:id>, where id is the id of a user in the database. The function takes the id, connects to the database, and retrieve the user with that id. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", [id])
        row = cursor.fetchone()
        res = jsonify(row)
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# POST users
@app.route('/api/users', methods=['POST'])
def add_users():
    """
    An implementation of a POST method to create an entry in the users table in the database.

    The function is called when a POST request is received with the url /api/users. A json body is expected with the PUT request. The function takes the body content, connects to the database, and create a new user. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        _json = request.json
        _id = _json['id']
        _username = _json['username']
        _firstname = _json['firstname']
        _lastname = _json['lastname']
        _pwd = _json['pwd']
        _salt = _json['salt']
        _gmail = _json['gmail']
        _userType = _json['userType']
        _macAd = _json['macAd']
        _gg_id = _json['gg_id']
        
        # insert record in database
        sqlQuery = "INSERT INTO users(id, username, firstname, lastname, pwd, salt, gmail, userType, macAd, gg_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (_id, _username, _firstname, _lastname, _pwd, _salt, _gmail, _userType, _macAd, _gg_id,)
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        cursor.execute(sqlQuery, data)
        # conn.commit()
        mysql.connection.commit()
        res = jsonify('User created successfully.')
        res.status_code = 200

        return res
        cursor.close() 
    except Exception as e:
        print(e)
    else:
        return not_found()
    # finally:
    #     cursor.close() 
        # conn.close()

# PUT users
@app.route('/api/users', methods=['PUT'])
def update_users():
    """
    An implementation of a PUT method to update an entry in the users table in the database.

    The function is called when a PUT request is received with the url /api/users. A json body with the proper users id is expected with the PUT request. The function takes the body content, connects to the database, and update the respective user. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        _json = request.json
        _id = _json['id']
        _username = _json['username']
        _firstname = _json['firstname']
        _lastname = _json['lastname']
        _pwd = _json['pwd']
        _salt = _json['salt']
        _gmail = _json['gmail']
        _userType = _json['userType']
        _macAd = _json['macAd']
        _gg_id = _json['gg_id']
        
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        if _id and request.method == 'PUT':
            # update record in database
            sql = "UPDATE users SET username=%s, firstname=%s, lastname=%s, pwd=%s, salt=%s, gmail=%s, userType=%s, macAd=%s, gg_id=%s WHERE id=%s"
            data = (_username, _firstname, _lastname, _pwd, _salt, _gmail, _userType, _macAd, _gg_id, _id,)
            cursor.execute(sql, data)
            # conn.commit()
            mysql.connection.commit()
            res = jsonify('User updated successfully.')
            res.status_code = 200
            return res
        else:
            return not_found()
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# DELETE user		
@app.route('/api/users/<string:id>', methods=['DELETE'])
def delete_users(id):
    """
    An implementation of a DELETE method to delete an entry from the users table in the database.

    The function is called when a DELETE request is received with the url /api/users/<string:id>, where id is the id of a user in the database. The function takes the id, connects to the database, and deletes the user with that id. A confirmation json message is returned.  

    Arguments:
        string id: the id of the user in the database.

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", [id])
        # conn.commit()
        mysql.connection.commit()
        res = jsonify('User deleted successfully.')
        res.status_code = 200
        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# GET issues
@app.route('/api/issues')
def get_issues():
    """
    An implementation of a GET method to retrieve all entries in the issues table in the database.

    The function is called when a GET request is received with the url /api/issues. The function connects to the database, and retrieve all issues. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM issues")
        issues = cursor.fetchall()
        res = jsonify(issues)
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# GET issues BY ID
@app.route('/api/issues/<string:id>')
def get_issue(id):
    """
    An implementation of a GET method to retrieve an entry by id in the issues table in the database.

    The function is called when a GET request is received with the url /api/issues/<string:id>, where id is the id of an issue in the database. The function takes the id, connects to the database, and retrieve the issue with that id. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM issues WHERE id=%s", [id])
        row = cursor.fetchone()
        res = jsonify(row)
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# POST issues
@app.route('/api/issues', methods=['POST'])
def add_issues():
    """
    An implementation of a POST method to create an entry in the issues table in the database.

    The function is called when a POST request is received with the url /api/issues. A json body is expected with the PUT request. The function takes the body content, connects to the database, and create a new issue. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        _json = request.json
        _id = _json['id']
        _carId = _json['carId']
        _issueDetail = _json['issueDetail']
        _longitude = _json['longitude']
        _latitude = _json['latitude']
        _timeNdate = _json['timeNdate']
        _issueStatus = _json['issueStatus']
        
        # insert record in database
        sqlQuery = "INSERT INTO issues(id, carId, issueDetail, longitude, latitude, timeNdate, issueStatus) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        data = (_id, _carId, _issueDetail, _longitude, _latitude, _timeNdate, _issueStatus,)
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        cursor.execute(sqlQuery, data)
        # conn.commit()
        mysql.connection.commit()
        res = jsonify('Issue created successfully.')
        res.status_code = 200

        return res
        cursor.close()
    except Exception as e:
        print(e)
    else:
        return not_found()
    # finally:
    #     cursor.close() 
        # conn.close()

# PUT issues
@app.route('/api/issues', methods=['PUT'])
def update_issues():
    """
    An implementation of a PUT method to update an entry in the issues table in the database.

    The function is called when a PUT request is received with the url /api/issues. A json body with the proper issue id is expected with the PUT request. The function takes the body content, connects to the database, and update the respective issue. A confirmation json message is returned.  

    Return:
        res: a json message.
    """

    try:
        _json = request.json
        _id = _json['id']
        _carId = _json['carId']
        _issueDetail = _json['issueDetail']
        _longitude = _json['longitude']
        _latitude = _json['latitude']
        _timeNdate = _json['timeNdate']
        _issueStatus = _json['issueStatus']
        
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        if _id and request.method == 'PUT':
            # update record in database
            sql = "UPDATE issues SET carId=%s, issueDetail=%s, longitude=%s, latitude=%s, timeNdate=%s, issueStatus=%s WHERE id=%s"
            data = (_carId, _issueDetail, _longitude, _latitude, _timeNdate, _issueStatus, _id,)
            cursor.execute(sql, data)
            # conn.commit()
            mysql.connection.commit()
            res = jsonify('Issue updated successfully.')
            res.status_code = 200
            return res
        else:
            return not_found()
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

# DELETE issue		
@app.route('/api/issues/<string:id>', methods=['DELETE'])
def delete_issues(id):
    """
    An implementation of a DELETE method to delete an entry from the issues table in the database.

    The function is called when a DELETE request is received with the url /api/issues/<string:id>, where id is the id of an issue in the database. The function takes the id, connects to the database, and deletes the issue with that id. A confirmation json message is returned.  

    Arguments:
        string id: the id of the issue in the database.

    Return:
        res: a json message.
    """

    try:
        # conn = open_connection()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM issues WHERE id=%s", [id])
        # conn.commit()
        mysql.connection.commit()
        res = jsonify('Issue deleted successfully.')
        res.status_code = 200
        return res
        cursor.close()
    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
        # conn.close()

@app.errorhandler(404)
def not_found(error=None):
    """
    Return a 404 error.

    Return:
        res: a json message.
    """

    message = {
        'status': 404,
        'message': 'There is no record: ' + request.url,
    }
    res = jsonify(message)
    res.status_code = 404

    return res

# <--------------------------------------------------->
#                   Calendar Components

# # Add Calendar Event Form Class
# class AddEvent(Form):
#     eventName = StringField('eventName', [validators.Length(max=255)])
#     sTime = StringField('sTime', [validators.Length(max=19)])
#     eTime = StringField('eTime', [validators.Length(max=19)])
#     cid = StringField('cid', [validators.Length(max=255)])

# #Begin flask route
# @app.route('/calendar', methods=['GET', 'POST'])
# def calendar():
#     if 'credentials' not in flask.session:
#       return flask.redirect(flask.url_for('oauth2callback'))
#     credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
#     if credentials.access_token_expired:
#         return flask.redirect(flask.url_for('oauth2callback'))
#     calendars=getCalendars()

#     form = AddEvent(request.form, obj=calendars)
#     if request.method == 'POST' and form.validate():
#         name = form.eventName.data
#         sTime = parser.parse(form.sTime.data)
#         eTime = parser.parse(form.eTime.data)
#         cid = form.cid.data

#         sConverted = rfc3339(sTime)
#         eConverted = rfc3339(eTime)
#         oauth(name, cid, sConverted, eConverted)
#     return flask.render_template('calendar.html', calendars=calendars, form=form)

# #Begin oauth callback route
# @app.route('/oauth2callback')
# def oauth2callback():
#   flow = client.flow_from_clientsecrets(
#       'client_secrets.json',
#       scope='https://www.googleapis.com/auth/calendar',
#       redirect_uri=flask.url_for('oauth2callback', _external=True))
#   if 'code' not in flask.request.args:
#     auth_uri = flow.step1_get_authorize_url()
#     return flask.redirect(auth_uri)
#   else:
#     auth_code = flask.request.args.get('code')
#     credentials = flow.step2_exchange(auth_code)
#     flask.session['credentials'] = credentials.to_json()
#     return flask.redirect(flask.url_for('calendar'))

# # Gets the calendar names and their corresponding ID's
# def getCalendars():
#     calendars = []
#     try:
#         credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
#     except credError:
#         print("did not assign credentials")
#     http_auth = credentials.authorize(httplib2.Http())
#     service = discovery.build('calendar', 'v3', http_auth)
#     page_token = None
#     while True:
#       calendar_list = service.calendarList().list(pageToken=page_token).execute()
#       for calendar_list_entry in calendar_list['items']:
#         calendars.append({"name": calendar_list_entry['summary'], "id": calendar_list_entry['id']})
#       page_token = calendar_list.get('nextPageToken')
#       if not page_token:
#         break
#     return calendars

# #Function to add event into calendar selected
# def oauth(name, cid, sTime, eTime):
#     print(sTime)
#     print(eTime)
#     print(name)
#     print(cid)
#     try:
#         credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
#     except credError:
#         print("did not assign credentials")
#     http_auth = credentials.authorize(httplib2.Http())
#     service = discovery.build('calendar', 'v3', http_auth)
#     eventName = ""
#     event = {
#         'summary': name,
#         'start': {
#         'dateTime': sTime
#         },
#         'end': {
#         'dateTime': eTime
#         },
#         'iCalUID': 'originalUID'
#     }
#     imported_event = service.events().import_(calendarId=cid, body=event).execute()
#     print("Succesfully Imported Event")
#     return flask.redirect(flask.url_for('calendar'))

if __name__ == '__main__':
    app.run(debug=True)