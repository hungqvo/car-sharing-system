import requests
import json

# Unit test for REST API in Part A (users, cars, bookings, issues)    
    
# TEST POST

def test_post_users_headers_body_json():
    url = 'https://carshare-289209.df.r.appspot.com/api/users'
    
    # Additional headers.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    # Body
    payload = {
            "firstname": "abc d",
            "gg_id": "abc d",
            "gmail": "abc d",
            "id": "abc d",
            "lastname": "abc d",
            "macAd": "abc d",
            "pwd": "abc d",
            "salt": "abc d",
            "userType": "abc d",
            "username": "abc d"
        }
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.post(url, headers=headers, data=json.dumps(payload,indent=4))       
    
    # Validate status code if request is successful, response results in code 200
    assert resp.status_code == 200

def test_post_cars_headers_body_json():
    url = 'https://carshare-289209.df.r.appspot.com/api/cars'
    
    # Additional headers.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    # Body
    payload = {
            "bodyType": "abc d",
            "carCode": "abc d",
            "carImage": "abc d",
            "carLocation": "abc d",
            "carName": "abc d",
            "carStatus": "abc d",
            "colour": "abc d",
            "costPerHour": 1,
            "id": "abc d",
            "make": "abc d",
            "seats": 1
        }
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.post(url, headers=headers, data=json.dumps(payload,indent=4))       
    
    # Validate status code if request is successful, response results in code 200
    assert resp.status_code == 200

def test_post_bookings_headers_body_json():
    url = 'https://carshare-289209.df.r.appspot.com/api/bookings'
    
    # Additional headers.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    # Body
    payload = {
            "id": "abc d",
            "cid": "",
            "eid": "",
            "userId": "abc d",
            "carId": "abc d",
            "bookingDate": "abc d",
            "timeFrom": "abc d",
            "nOHours": 1
        }
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.post(url, headers=headers, data=json.dumps(payload,indent=4))       
    
    # Validate status code if request is successful, response results in code 200
    assert resp.status_code == 200

def test_post_issues_headers_body_json():
    url = 'https://carshare-289209.df.r.appspot.com/api/issues'
    
    # Additional headers.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    # Body
    payload = {
            "id": "abc d",
            "carId": "abc d",
            "issueDetail": "abc d",
            "longitude": 0,
            "latitude": 0,
            "timeNdate": "abc d",
            "issueStatus": "abc d"
        }
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.post(url, headers=headers, data=json.dumps(payload,indent=4))       
    
    # Validate status code if request is successful, response results in code 200
    assert resp.status_code == 200

# TEST GET

def test_get_users_check_status_code_equals_200():
    response = requests.get("https://carshare-289209.df.r.appspot.com/api/users")
    assert response.status_code == 200

def test_get_cars_check_status_code_equals_200():
    response = requests.get("https://carshare-289209.df.r.appspot.com/api/cars")
    assert response.status_code == 200

def test_get_bookings_check_status_code_equals_200():
    response = requests.get("https://carshare-289209.df.r.appspot.com/api/bookings")
    assert response.status_code == 200

def test_get_issues_check_status_code_equals_200():
    response = requests.get("https://carshare-289209.df.r.appspot.com/api/issues")
    assert response.status_code == 200

# TEST GET BY ID

def test_get_user_check_status_code_equals_200():
    response = requests.get("https://carshare-289209.df.r.appspot.com/api/users/abc d")
    response_body = response.json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == "application/json"
    assert response_body["id"] == "abc d"
    assert response_body["username"] == "abc d"

def test_get_car_check_status_code_equals_200():
    response = requests.get("https://carshare-289209.df.r.appspot.com/api/cars/abc d")
    response_body = response.json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == "application/json"
    assert response_body["id"] == "abc d"
    assert response_body["carCode"] == "abc d"
    assert response_body["seats"] == 1

def test_get_booking_check_status_code_equals_200():
    response = requests.get("https://carshare-289209.df.r.appspot.com/api/bookings/abc d")
    response_body = response.json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == "application/json"
    assert response_body["id"] == "abc d"
    assert response_body["carId"] == "abc d"
    assert response_body["userId"] == "abc d"

def test_get_issue_check_status_code_equals_200():
    response = requests.get("https://carshare-289209.df.r.appspot.com/api/issues/abc d")
    response_body = response.json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == "application/json"
    assert response_body["id"] == "abc d"
    assert response_body["carId"] == "abc d"

# TEST PUT

def test_put_users_headers_body_json():
    url = 'https://carshare-289209.df.r.appspot.com/api/users'
    
    # Additional headers.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    # Body
    payload = {
            "firstname": "abc de",
            "gg_id": "abc de",
            "gmail": "abc de",
            "id": "abc d",
            "lastname": "abc de",
            "macAd": "abc de",
            "pwd": "abc de",
            "salt": "abc de",
            "userType": "abc de",
            "username": "abc de"
        }
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.put(url, headers=headers, data=json.dumps(payload,indent=4))       
    
    # Validate status code if request is successful, response results in code 200
    assert resp.status_code == 200

def test_put_cars_headers_body_json():
    url = 'https://carshare-289209.df.r.appspot.com/api/cars'
    
    # Additional headers.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    # Body
    payload = {
            "bodyType": "abc de",
            "carCode": "abc de",
            "carImage": "abc de",
            "carLocation": "abc de",
            "carName": "abc de",
            "carStatus": "abc de",
            "colour": "abc de",
            "costPerHour": 100,
            "id": "abc d",
            "make": "abc de",
            "seats": 10
        }
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.put(url, headers=headers, data=json.dumps(payload,indent=4))       
    
    # Validate status code if request is successful, response results in code 200
    assert resp.status_code == 200

def test_put_bookings_headers_body_json():
    url = 'https://carshare-289209.df.r.appspot.com/api/bookings'
    
    # Additional headers.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    # Body
    payload = {
            "id": "abc d",
            "cid": "",
            "eid": "",
            "userId": "abc d",
            "carId": "abc d",
            "bookingDate": "abc de",
            "timeFrom": "abc",
            "nOHours": 10
        }
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.put(url, headers=headers, data=json.dumps(payload,indent=4))       
    
    # Validate status code if request is successful, response results in code 200
    assert resp.status_code == 200

def test_put_issues_headers_body_json():
    url = 'https://carshare-289209.df.r.appspot.com/api/issues'
    
    # Additional headers.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    # Body
    payload = {
            "id": "abc d",
            "carId": "abc d",
            "issueDetail": "abc de",
            "longitude": 1,
            "latitude": 1,
            "timeNdate": "abc de",
            "issueStatus": "abc de"
        }
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.put(url, headers=headers, data=json.dumps(payload,indent=4))       
    
    # Validate status code if request is successful, response results in code 200
    assert resp.status_code == 200

# TEST DELETE

def test_delete_bookings_check_status_code_equals_200():
    response = requests.delete("https://carshare-289209.df.r.appspot.com/api/bookings/acb d")
    assert response.status_code == 200

def test_delete_issues_check_status_code_equals_200():
    response = requests.delete("https://carshare-289209.df.r.appspot.com/api/issues/acb d")
    assert response.status_code == 200 

def test_delete_users_check_status_code_equals_200():
    response = requests.delete("https://carshare-289209.df.r.appspot.com/api/users/acb d")
    assert response.status_code == 200

def test_delete_cars_check_status_code_equals_200():
    response = requests.delete("https://carshare-289209.df.r.appspot.com/api/cars/acb d")
    assert response.status_code == 200

# Cleaning up
def clean_up():
    requests.delete("https://carshare-289209.df.r.appspot.com/api/bookings/acb d")
    requests.delete("https://carshare-289209.df.r.appspot.com/api/issues/acb d")
    requests.delete("https://carshare-289209.df.r.appspot.com/api/users/acb d")
    requests.delete("https://carshare-289209.df.r.appspot.com/api/cars/acb d")

clean_up()