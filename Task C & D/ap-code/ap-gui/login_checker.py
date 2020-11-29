import requests
import os
from passlib.hash import sha256_crypt
import json
# from getpass import getpass

# Remember to create a parent folder named "images_folder" in the main "AgentPiConnector" directory for this script to later add more folders to store user images


# Create a class
class loginHandler:
    @classmethod
    def credential_check(cls, username, password):
        # print("login_checker: {} {}".format(username,password))
        try:
            imported_users = requests.get('http://carshare-289209.df.r.appspot.com/api/users')
            users = imported_users.json()
            
            for user in users:
                if user['username'] == username:
                    
                    stored_password = user['pwd']
                    salt = user['salt']
                    password_target = password + salt
                    if sha256_crypt.verify(password_target, stored_password):
                        authenticated_user=user
                        # print("Login verified")
                        userId = user['id']
                        length = len(userId)
                        last_digits = length - 5
                        last_digit_name = userId[last_digits:length]
                        first_name = user['firstname']
                        id_name = first_name + last_digit_name
                        user_dict ={
                            "userId": userId,
                            "userName": id_name
                        }
                        return user_dict
                        break
        except:
            # print("No user")
            return None
