import json
from app import app
import requests
import unittest

class FlaskTestCase(unittest.TestCase):
    def test_home_page(self):
        response = requests.get("http://localhost:5000/")
        self.assertEqual(response.status_code, 200)
    
    def test_engineer_map(self):
        response = requests.get("http://localhost:5000/engineer_manager")
        self.assertEqual(response.status_code, 200)

    def test_get_car_issues(self):
        response = requests.get("http://localhost:5000/get_car_issues")
        self.assertEqual(response.status_code, 200)
 
    def test_get_all_engineers(self):
        response = requests.get("http://localhost:5000/get_all_engineers")
        self.assertEqual(response.status_code, 200)

    def test_get_booking_by_car_code(self):
        response = requests.get("http://localhost:5000/get_booking_by_car_code/TEST")
        self.assertEqual(response.status_code, 200)

    def test_get_car_usage(self):
        response = requests.get("http://localhost:5000/get_car_usage")
        self.assertEqual(response.status_code, 200)

    def test_get_car_status_audit(self):
        response = requests.get("http://localhost:5000/get_car_status_audit")
        self.assertEqual(response.status_code, 200)

    def test_get_monthly_revenue(self):
        response = requests.get("http://localhost:5000/get_monthly_revenue/")
        self.assertEqual(response.status_code, 200)
    
    def test_issue_manager_page(self):
        response = requests.get("http://localhost:5000/issue_manager")
        self.assertEqual(response.status_code, 200)
    
    def test_car_manager_page(self):
        response = requests.get("http://localhost:5000/car_manager")
        self.assertEqual(response.status_code, 200)

    def test_user_manager_page(self):
        response = requests.get("http://localhost:5000/user_manager")
        self.assertEqual(response.status_code, 200)

    def test_remove_car_page(self):
        response = requests.get("http://localhost:5000/remove_car/testid")
        self.assertEqual(response.status_code, 200)

    def test_remove_user_page(self):
        response = requests.get("http://localhost:5000/remove_user/testid")
        self.assertEqual(response.status_code, 200)
    
    def test_fix_issue(self):
        response = requests.get("http://localhost:5000/fix_issue/testid")
        self.assertEqual(response.status_code, 200) 

    def test_update_car_page(self):
        response = requests.get("http://localhost:5000/update_car_page/testid")
        self.assertEqual(response.status_code, 200)

    def test_update_user_page(self):
        response = requests.get("http://localhost:5000/update_user_page/testid")
        self.assertEqual(response.status_code, 200)

    def test_update_user_api(self):
        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
        payload = {
            "firstname": "somefirstname",
            "gg_id": "someggid",
            "gmail": "somegmail",
            "id": "testid",
            "lastname": "somelastname",
            "macAd": "somemacad",
            "password": "somepwd",
            "salt": "77aa3edd22766057",
            "userType": "someusertype",
            "username": "someusername"
        }
        response = requests.put("http://localhost:5000/update_user/testid",headers=headers, data=json.dumps(payload,indent=4))
        self.assertEqual(response.status_code, 200)
    
    def test_add_issue(self):
        response = requests.get("http://localhost:5000/add_issue")
        self.assertEqual(response.status_code, 200)

    def test_add_car(self):
        response = requests.get("http://localhost:5000/add_car")
        self.assertEqual(response.status_code, 200)
    
    def test_add_user(self):
        response = requests.get("http://localhost:5000/add_user")
        self.assertEqual(response.status_code, 200)

    def test_search_user(self):
        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
        payload = {
            "keyWord": "bmw",
            "property": "username"
        }
        response = requests.post("http://localhost:5000/search-user",headers=headers, data=json.dumps(payload,indent=4))
        self.assertEqual(response.status_code, 200)

    def test_search_car(self):
        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
        payload = {
            "keyWord": "bmw",
            "property": "make",
            "condition": " "
        }
        response = requests.post("http://localhost:5000/search-car",headers=headers, data=json.dumps(payload,indent=4))
        self.assertEqual(response.status_code, 200)

    def test_get_all_booking_history(self):
        response = requests.get("http://localhost:5000/get-all-booking-history")
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = requests.get("http://localhost:5000/login")
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard(self):
        response = requests.get("http://localhost:5000/dashboard")
        self.assertEqual(response.status_code, 200) 




    





    
suite = unittest.TestLoader().loadTestsFromTestCase(FlaskTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)