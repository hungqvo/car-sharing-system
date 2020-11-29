### REFERENCE: https://www.w3schools.com/python/python_dictionaries.asp

import requests
import json

# Create a class
class EngineerInfoChecker:
    
    @classmethod
    def get_engineer_by_id(cls,eng_Id):
        # Get user's booking detail through given booking ID
        res = requests.get('http://carshare-289209.df.r.appspot.com/api/users/' + eng_Id)
        try:
            # Engineer detail
            engineer = res.json()
            engineer_dictionary = {
                "firstName": engineer['firstname'],
                "lastName": engineer['lastname'],
                "userName": engineer['id'],
                "userType": engineer['userType']
            }
        except:
            print("No engineer profile")
        return engineer_dictionary