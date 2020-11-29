import pymysql
import datetime
from app import app
from config import mysql
from flask import jsonify
from flask import flash, request, render_template, redirect, url_for, session, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask_httpauth import HTTPBasicAuth
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import math
from functools import wraps
import hashlib
import os
import uuid
import smtplib, ssl
import json
import cloudstorage
from google.cloud import storage
import os
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
auth = HTTPBasicAuth()
load_dotenv(verbose=True)
env_path = os.getcwd()
load_dotenv(dotenv_path= env_path + '/.env')
GoogleMaps(app)
from passlib.hash import sha256_crypt
"""
Part Admin Webpage and Admin API
--------------------------------
This document is solely for the admin management(Part B)

Summary.
This part of the code basically load the html page and interact with database
"""
#wrap the login state in the session
#users dont need to login again in their computer
def is_logged_in(f):
    """
    This function will wrap the login state in the session
    So users dont need to login again in their computer 
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


#engineer page includes a google map with issue-marker
@app.route('/engineer_manager')
@is_logged_in
def engineer_mana():
    """
    This function will load the engineer manager page
    And retrieve those issues with need-repair status
    finally display it on the map with the marker allocate the location of the issue
    """
# creating a map in the view
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
#get all issue, car related information
    cursor.execute("""Select issues.longitude, issues.latitude, issues.issueStatus,
    cars.carCode, cars.make, cars.bodyType, cars.colour from issues join cars on issues.carId = cars.id""")
    recordRow = cursor.fetchall() 
    markersArray = []
    for i in recordRow:
#only show those issues have not fixed yet
        if i["issueStatus"] == "need-repair":
            markersArray.append({
            'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
            'lat': i["latitude"],
            'lng': i["longitude"],
#display issue information on the inforbox
            'infobox': "<b>Car code: %s %s %s</b>" %(i["colour"], i["bodyType"], i["make"])
            })
#init map constructor
    sndmap = Map(
        identifier="sndmap",
        lat=10.728916,
        lng=106.695777,
        markers=markersArray,
        style="height:600px;width:1200px;margin:0;",
        zoom=10
    )
    
    return render_template('engineer.html', sndmap=sndmap)
#get_car_issues api
@app.route('/get_car_issues')
def get_car_issues():
    """
    This is get api with localhost:5000/get_car_issues
    return all the car issues information includes 
    longitue, latitude, status, car code, brand, body type, colour of the car
    """
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""Select issues.longitude, issues.latitude, issues.issueStatus,
        cars.carCode, cars.make, cars.bodyType, cars.colour from issues join cars on issues.carId = cars.id""")
        recordRow = cursor.fetchall() 
        response = jsonify(recordRow)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
#load home page
@app.route('/', methods =['GET'])
def index():
    """
    This route will load the home page template
    """
    return render_template('home.html')
#get all engineer api
@app.route('/get_all_engineers', methods=['GET'])
def get_all_engineers():
    """
    This is get api with url: localhost:5000/get_all_engineers
    return list of engineers information includes 
    username, first name, last name, mail, mac address, user type
    """
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
    # select the newest records
        cursor.execute("Select * from users where users.userType = 'engineer'")
        recordRow = cursor.fetchall()
        response = jsonify(recordRow)
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        print(e)


#get booking car by car code api
@app.route('/get_booking_by_car_code/<string:carcode>', methods = ['GET'])
def get_booking_by_car_code(carcode):
    """
    This is get api with the url: localhost:5000/get_booking_car_code/somecarcode
    return the booking information includes
    user id, booking date, starting time, ending time, number of hours
    """
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """Select users.id, bookings.bookingDate, bookings.timeFrom, 
        bookings.timeTo, bookings.nOHours from cars inner join bookings on 
        bookings.carId = cars.id inner join users on bookings.userId = users.id 
        where cars.carCode = %s and cars.carStatus = %s"""
        values = (carcode,"booked")
        cursor.execute(query,values)
        result = cursor.fetchone()
        response = jsonify(result)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
#get car frequency usage api
@app.route('/get_car_usage',methods = ['GET'])
#@auth.login_required
def get_car_usage():
    """
    This is get api with the url: localhost:5000/get_car_usage
    counting the number of time each cars was booked then
    return brand of the car with the number of time booked
    """
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select cars.make as label, count(*) as y from bookings left join cars on cars.id = bookings.carId group by cars.make order by count(*) DESC ")
        result = cursor.fetchall()
        response = jsonify(result)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
        
@app.route('/get_car_usage_audit', methods = ['GET'])
def get_car_usage_audit():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""Select  cars.make, cars.bodyType, count(*) from bookings
        join cars on bookings.carId = cars.id group by cars.make, cars.bodyType limit 10""")
        result = cursor.fetchall()
        respone = jsonify(result)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
#get current car status api
@app.route('/get_car_status_audit', methods = ['GET'])
def get_car_status_audit():
    """ 
    This is get api with the url: localhost:5000/get_car_status_audit
    return the current number of cars are in different status such as booked, on-use, available, need-repair
    """
    
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select count(*) as y from cars where cars.carStatus = 'booked'")
        bookedCar = cursor.fetchone()
        cursor.execute("Select count(*) as y from cars where cars.carStatus = 'on-use'")
        onUse = cursor.fetchone()
        cursor.execute("Select count(*) as y from cars where cars.carStatus = 'available or cars.carStatus is null'")
        avaiCar = cursor.fetchone()
        cursor.execute("Select count(*) as y from cars where cars.carStatus = 'need-repair'")
        pendingCar = cursor.fetchone()
        response = jsonify([{'label': 'available', 'y': avaiCar['y']},{'label': 'booked', 'y': bookedCar['y']}, {'label': 'on-use','y':onUse['y']},{'label': 'nedd-repair', 'y': pendingCar['y']}])
        # response = jsonify({"available":avaiCar,"booked":bookedCar, "on-use":onUse, "need-repair":pendingCar})
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        print(e)
#get revenue of each month in this year
@app.route('/get_monthly_revenue/', methods = ['GET'])
def get_monthly_revenue():
    """
    This is get api with the url: localhost:5000/get_monthly_revenue
    return revenue of each month this year
    """

    try:
        
        conn = mysql.connect()
        cursor =conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""Select cars.costPerHour, 
        bookings.nOHours, bookings.bookingDate 
        from bookings join cars on cars.id = bookings.carID""")
        recordRow = cursor.fetchall()
        array =[0,0,0,0,0,0,0,0,0,0,0,0]
        months = ["01","02","03","04","05","06","07","08","09","10","11","12"]
        for i in range(len(months)):
            for j in recordRow:
                if j["bookingDate"].split("-")[0] == months[i]:
                    array[i] += j["costPerHour"]*j["nOHours"] 
        response = jsonify({"revenue":array})
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        print(e)
#load issue manager page
@app.route('/issue_manager', methods= ['GET', 'POST'])
@is_logged_in
def get_all_issues():
    """
    This route will load the issues management page
    """
    return render_template('issuelist.html', issues= get_all_issues_private())
#load car manager page
@app.route('/car_manager', methods= ['GET','POST'])
@is_logged_in
def get_all_car():
    """
    This route will load the car management page
    there are a form which help admin to search the car by keyword, property and condition (for cost per hour)
    after getting the admin input, it will return the search result based on the data base and the key word
    """
    if request.method == 'POST':
        keyWord = request.form['keyWord']
        property = request.form['property'] 
        if keyWord == ' ' or property == ' ':
           return render_template('carlist.html', cars=  get_all_cars_private())
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * from cars")
        result = cursor.fetchall()
        result_array =[]
        for i in result:
            if property == "seats" and keyWord == int(i[property]):
                result_array.append(i)
            elif property == "costPerHour" and request.form['condition'] != None and request.form['condition'] == "greater" and i['costPerHour'] >= int(keyWord):
                result_array.append(i) 
            elif property == "costPerHour" and request.form['condition'] != None and request.form['condition'] == "less" and i['costPerHour'] < int(keyWord):
                result_array.append(i)
            elif property != "seats" and property != "costPerHour":
                if keyWord.lower() in i[property].lower():
                    result_array.append(i)
        if result_array == []:
            cursor.close()
            conn.close()
            return render_template('carlist.html', cars= result_array)
        else:
            cursor.close()
            conn.close()
            return render_template('carlist.html', cars= result_array)
    
    return render_template('carlist.html', cars= get_all_cars_private()) 

def get_all_issues_private():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select cars.carCode as carCode, cars.make as make, cars.bodyType as bodyType, cars.colour as colour, issueDetail, timeNdate, issueStatus, issues.id from issues join cars on issues.carId = cars.id")
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)

def get_all_cars_private():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * from cars")
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)
#get user manager page
@app.route('/user_manager',methods = ['GET','POST'])
@is_logged_in
def get_all_user():
    """
    This route will load the user management page
    there are a form which help admin to search the user by key word and property
    after getting the admin input, it will return the search result based on the data base and the key word
    """
    if request.method == 'POST': 
        keyWord = request.form['keyWord']
        if keyWord == "":
           return render_template('userlist.html', users= get_all_users_private()) 
        property= request.form['property']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * from users")
        result = cursor.fetchall()
        result_array =[]
        for i in result:
            if keyWord.lower() in i[property].lower():
                result_array.append(i)
        if result_array == []:
            cursor.close()
            conn.close()
            print(result_array)
            return render_template("userlist.html", users=[])
        else:
            cursor.close()
            conn.close()
            return render_template("userlist.html", users=result_array)
        
    return render_template('userlist.html', users= get_all_users_private())
#get all engineer api
@app.route('/get_all_engineer', methods =['GET'])
def get_all_engineer():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
    # select the newest records
        cursor.execute("Select * from users where users.userType = 'engineer'")
        recordRow = cursor.fetchall()
        #response = jsonify(recordRow)
        #esponse.status_code = 200
        cursor.close()
        conn.close()
        return recordRow
    except Exception as e:
        print(e)
#remove car by id then load car manager page
@app.route('/remove_car/<string:id>', methods = ['GET','DELETE'])
@is_logged_in
def remove_car(id):
    """
    This route will remove the car with the given id
    after successfully remove, it will load the car management page
    """
    if id != None:
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = """Delete from cars where cars.id = %s"""
            values = (id)
            cursor.execute(query, values)
            conn.commit()
            cursor.execute("Select * from cars")
            recordRow = cursor.fetchall()
            cursor.close()
            conn.close()
            flash('You have just deleted a car successfully', 'success')
            return render_template('carlist.html', cars = recordRow)
        except Exception as e:
            print(e)
    else:
        return not_found()
#remove user then load user manager page
@app.route('/remove_user/<string:id>', methods = ['DELETE', 'GET'])
@is_logged_in
def remove_user(id):
    """
    This route will remove the user with the given id
    after successfully remove, it will load the user management page
    """
    if id != None:
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = """Delete from users where users.id = %s"""
            values = (id)
            cursor.execute(query, values)
            conn.commit()
            cursor.execute("Select * from users")
            recordRow = cursor.fetchall()
            cursor.close()
            conn.close()
            flash('You just delete an user successfully', 'success')
            return render_template('userlist.html', users = recordRow)
        except Exception as e:
            print(e)
    else:
        return not_found()
#change status of the issue to fixed
@app.route('/fix_issue/<string:id>', methods=['GET','PUT'])
@is_logged_in
def fix_issue(id):
    """
    This route will update the status of the issues from need-repair to fixed
    then load the issue management page when updated successfully
    """
    if id != None:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        firstQuery = """ Select * from issues where issues.id = %s"""
        firstValue = (id)
        cursor.execute(firstQuery,firstValue)
        row = cursor.fetchone()
        
        secondQuery = """Update issues set carId = %s, issueDetail = %s,
                longitude = %s, latitude = %s, timeNdate = %s, issueStatus = %s where id = %s"""
        secondValues = (row['carId'], row['issueDetail'], row['longitude'], row['latitude'], row['timeNdate'], "fixed", id )
        cursor.execute(secondQuery, secondValues)
        conn.commit()
        
        thirdQuery = """Update cars set carStatus = 'available' where id=%s"""
        thirdValue = (row['carId'])
        cursor.execute(thirdQuery, thirdValue)
        conn.commit()
        cursor.close()
        conn.close()
        flash('You have just fixed an issue successfully', 'success')
        return render_template('issuelist.html', issues= get_all_issues_private())
        
    else:
        return not_found()
#load update car page, then update the car then load car manager page
@app.route('/update_car_page/<string:id>', methods = ['GET','PUT', 'POST'])
@is_logged_in
def update_car_page(id):
    """
    This route load the update car page, it includes a form for admin input
    after submitting the form it will update all the properties of the car with the given id
    then load the car management page when updated successfully
    """
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
# select the newest records
    query = """Select * from cars where cars.id = %s"""
    value = (id)
    cursor.execute(query,value)
    recordRow = cursor.fetchone()
    cursor.close()
    conn.close()
    if request.method == 'POST':
        carCode = request.form['carCode']
        make = request.form['make']
        bodyType = request.form['bodyType']
        seats = request.form['seats']
        colour = request.form['colour']
        costPerHour = request.form['costPerHour']
        carLocation = request.form['carLocation']
        carStatus = request.form['carStatus']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """Update cars set carCode = %s, make = %s, bodyType =%s, 
                seats = %s, colour = %s, costPerHour = %s, carLocation = %s, carStatus = %s where id =%s"""
        values = (carCode, make, bodyType, seats, colour, costPerHour, carLocation, carStatus, id)
        cursor.execute(query,values)
        conn.commit()
        cursor.close()
        conn.close()
        flash('You have just updated a car successfully ', 'success')
        return render_template('carlist.html', cars= get_all_cars_private())
    
    return render_template('updatecar.html', car=recordRow) 
#load update user page, then update the userthen load user manager page
@app.route('/update_user_page/<string:id>', methods= ['GET','POST'])
@is_logged_in
def update_user_page(id):
    """
    This route load the update user page, it includes a form for admin input
    after submitting the form it will update all the properties of the user with the given id
    then load the car management page when updated successfully
    """
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
# select the newest records
    query = """Select * from users where users.id = %s"""
    value = (id)
    cursor.execute(query,value)
    recordRow = cursor.fetchone()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        gmail = request.form['gmail']
        password = request.form['password']
        salt = request.form['salt']
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),bytes.fromhex(salt) , 100000).hex()
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """Update users set username = %s, firstname = %s, lastname =%s, 
                pwd = %s, salt = %s, gmail = %s where id =%s"""
        values = (username, firstname, lastname, hashed, salt, gmail, id)
        cursor.execute(query,values)
        conn.commit()
        cursor.close()
        conn.close()
        flash('You have just updated an user successfully', 'success')
        return render_template('userlist.html', users=get_all_users_private())
        
    return render_template('updateuser.html', user=recordRow)
def get_all_users_private():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
    # select the newest records
        cursor.execute("Select * from users")
        recordRow = cursor.fetchall()
        cursor.close()
        conn.close()
        return recordRow
    except Exception as e:
        print(e)

#update user then load the user manager page
@app.route('/update_user/<string:id>', methods = ['PUT'])
def update_user(id):
    if id != None:
        try:
            _json = request.json
            if 'firstname' in _json and 'lastname' in _json and 'username' in _json and 'password' in _json and 'gmail' in _json and 'salt' in _json:
                firstname = _json['firstname']
                lastname = _json['lastname']
                username = _json['username']
                password = _json['password']
                gmail = _json['gmail']
                salt = _json['salt']
                hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),bytes.fromhex(salt) , 100000).hex()
                conn = mysql.connect()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                query = """Update users set username = %s, firstname = %s, lastname =%s, 
                        pwd = %s, salt = %s, gmail = %s where id =%s"""
                values = (username, firstname, lastname, hashed, salt, gmail, id)
                cursor.execute(query,values)
                conn.commit()
                response = jsonify({"message":"Update user successfully"})
                response.status_code = 200
                cursor.close()
                conn.close()
                return response
            else:
                return not_found()
        except Exception as e:
            print(e)
#load the crate issue page then load issue manager page afterthat
@app.route('/add_issue', methods = ['GET','POST'])
@is_logged_in
def add_issuse():
    """
    This route will load the add issues page with the form for admin input( issue information)
    after submitting the form, it will create an issue
    then load the issues management page
    """
    if request.method == "POST":
        message = MIMEMultipart()
        message["Subject"] = "Car issue"
        message.attach(MIMEText("Access this link to see the car location: http://localhost:5000/engineer_manager", "plain"))
        text = message.as_string()
        carCode = request.form['carCode']
        issueDetail = request.form['issueDetail']
        location = request.form['location']
        geolocator = Nominatim(user_agent="Car Sharing System")
        geoLocation = geolocator.geocode(location)
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor) 
        firstQuery = """Select id from cars where cars.carCode = %s"""
        firstValue = (carCode)
        cursor.execute(firstQuery, firstValue)
        row = cursor.fetchone()

        secondQuery = """Update cars set carStatus =%s  where id = %s"""
        secondValue = ("need-repair", row['id'])
        cursor.execute(secondQuery, secondValue)
        conn.commit()
        query = """Insert into issues(id, carId, issueDetail, longitude, latitude, timeNdate, issueStatus)
                values (%s,%s,%s,%s,%s,%s, %s) """
        thisisID = uuid.uuid1()
        time=str(datetime.datetime.now()).split('.')[0]
        values = (str(thisisID), row['id'], issueDetail, geoLocation.longitude, geoLocation.latitude,time, "need-repair")
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query,values)
        conn.commit()
        cursor.close()
        conn.close()
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", os.getenv("MAIL_PORT"), context=context) as server:
            server.login("khanhniii07@gmail.com", os.getenv("ADMIN_PASS"))
            for i in get_all_engineer():
                server.sendmail("khanhniii07@gmail.com", i['gmail'], text)
        flash('You have just added an issue successfully', 'success') 
        return render_template('issuelist.html', issues= get_all_issues_private())
    return render_template('addissue.html')

#load add car page then create car in the database
@app.route('/add_car', methods = ['GET','POST'])
@is_logged_in
def add_car():
    """
    This route will load the add cars page with the form for admin input( car information)
    after submitting the form, it will create a car
    then load the cars management page
    """
    if request.method == 'POST':
        carCode = request.form['carCode']
        make = request.form['make']
        bodyType= request.form['bodyType']
        colour= request.form['colour']
        seats= request.form['seats']
        location= request.form['location']
        costPerHour= request.form['costPerHour']
        query = """Insert into cars (id, carCode, make, bodyType, colour, seats, carLocation, costPerHour, carStatus) 
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        thisisID = uuid.uuid1() 
        values = (str(thisisID), carCode, make, bodyType, colour, seats, location, costPerHour, "available")
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query,values)
        conn.commit()
        cursor.close()
        conn.close()
        flash('You just add a car successfully', 'success')
        return render_template('carlist.html', cars = get_all_cars_private())
        
    return render_template('addcar.html')
    
#load add user page then create user in the data base
@app.route('/add_user', methods = ['GET','POST'])
@is_logged_in
def add_user():
    """
    This route will load the add users page with the form for admin input( user information)
    after submitting the form, it will create an user
    then load the users management page
    """
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['pwd']
        gmail = request.form['gmail']
        macAd = request.form['macAd']
        userType = request.form['userType']
        salt = os.urandom(8).hex()
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),bytes.fromhex(salt) , 100000).hex()
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """ Insert into users (id, firstname, lastname, username,
                    pwd, salt, gmail, userType, macAd) Values 
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s) """
        thisisID = uuid.uuid1()
        values = (str(thisisID),firstname, lastname, username, hashed, salt, gmail,userType, macAd)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        flash('You just add an user successfully', 'success')
        return render_template('userlist.html', users= get_all_users_private())
    return render_template('adduser.html')
#search user by different properties with the keyword
@app.route('/search-user', methods = ['POST'])
def userSearch():
    try:
        _json = request.json
        keyWord = _json['keyWord']
        property = _json['property']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * from users where users.userType = 'user'")
        result = cursor.fetchall()
        result_array =[]
        for i in result:
            if keyWord.lower() in i[property].lower():
                result_array.append(i)
        if result_array == []:
            response = jsonify({"message": "Not Found"})
            response.status_code = 200
            cursor.close()
            conn.close()
            return response
        else:
            response = jsonify(result_array)
            response.status_code = 200
            cursor.close()
            conn.close()
            return response
    except Exception as e:
        print(e)
#search car by different properties and condition(apply for cost per hour) with the keyword        
@app.route('/search-car', methods = ['POST'])
def carSearch():
    try:
        _json = request.json
        if 'keyWord' in _json and 'property' in _json and 'condition' in _json:
            keyWord = _json['keyWord']
            property = _json['property']
            condition = _json['condition']
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("Select * from cars")
            result = cursor.fetchall()
            result_array =[]
            for i in result:
                if property == "seats" and keyWord == int(i[property]):
                    result_array.append(i)
                elif property == "costPerHour" and condition == "greater" and i['costPerHour'] >= keyWord:
                    result_array.append(i) 
                elif property == "costPerHour" and condition == "less" and i['costPerHour'] <= keyWord:
                    result_array.append(i)
                elif property != "seats" and property != "costPerHour":
                    if keyWord.lower() in i[property].lower():
                        result_array.append(i)
            if result_array == []:
                response = jsonify({"message": "Not Found"})
                response.status_code = 200
                cursor.close()
                conn.close()
                return response
            else:
                response = jsonify(result_array)
                response.status_code = 200
                cursor.close()
                conn.close()
                return response
        else:
            response = jsonify({"message": "Not Found"})
            response.status_code = 200
            cursor.close()
            conn.close()
            return response
    except Exception as e:
        print(e)
#get all booking history api
@app.route('/get-all-booking-history', methods = ['GET'])
def get_all_booking():
    """
    This is get api with the url: localhost:5000/get-all-booking-history
    return the user and car information related to the booking such as 
    firstname, lastname, car code, starting time, ending time
    """
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""select users.firstName, users.lastName, cars.carCode, 
                        bookings.timeFrom, bookings.timeTo from bookings 
                        join users on bookings.userId = users.id 
                        join cars on bookings.carId = cars.id;""")
        recordRow = cursor.fetchall()
        response = jsonify(recordRow)
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        print(e)


#remove the login session then redirect to login page
@app.route('/logout')
def logout():
    """
    This route will remove the login in session
    then redirect to the login page
    """
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
#load login page, take the request params then verify it
#if success, store the session then laod the home page for different type of user
#if not success, load the login page again
@app.route('/login', methods = ['GET', 'POST'])
def login():
    """
    This route will load the login page with the login form(username and password)
    after submitting the form, it will verify the user authentication 
    if the password and username are matched, it will load different landing page corresponded to that type of user
    if not matched it will laod the login page again
    """
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        result = cursor.execute("Select * from users where username = %s", [username])
        if result >0:
            data = cursor.fetchone()
            password = data['pwd']
            # new_key = hashlib.pbkdf2_hmac('sha256', password_candidate.encode('utf-8'), bytes.fromhex(data['salt']), 100000)
            password_target = password_candidate+data['salt']
            if sha256_crypt.verify(password_target, password):
                session['logged_in'] = True
                session['username'] = username
                if data['userType'] == 'admin':
                    session['userType'] = 'admin'
                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))
                elif data['userType'] == 'manager':
                    session['userType'] = 'manager'
                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))
                elif data['userType'] == 'engineer':
                    session['userType'] = 'engineer'
                    flash('You are now logged in', 'success')
                    return redirect(url_for('engineer_mana'))
                else:
                    error = 'You donot have a right to access this page'
                    return render_template('login.html', error=error)
            else:
                error = 'Username or password is invalid'
                return render_template('login.html', error=error)
        else:
            error = 'Username or password is invalid'
            return render_template('login.html', error=error)

    return render_template('login.html')
#load dashboard page
@app.route('/dashboard')
@is_logged_in
def dashboard():
    """
    This route will load the dashboard page
    """
    return render_template('dashboard.html')

@auth.verify_password
def authen(username, password):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select users.pwd, users.salt, users.userType from users where username = %(username)s", {'username':username})
    recordRow = cursor.fetchone()
    #result = jsonify(recordRow)
    if recordRow != None:
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(recordRow['salt']), 100000)
        if new_key.hex() == recordRow['pwd']:
            return True
        else:
            return False
    else:
        return False
    
@app.errorhandler(404)
# handling the error that makes the incorrect request
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone
#secret key for the session
app.secret_key = os.getenv('SECRET_KEY')
if __name__ == '__main__':
    app.run(debug=True)