import requests
import os
from passlib.hash import sha256_crypt
from getpass import getpass

# Remember to create a parent folder named "images_folder" in the main "AgentPiConnector" directory for this script to later add more folders to store user images

# Function get all users in db
def get_users():
    users = []
    res = requests.get('https://my-project-1551900810701.df.r.appspot.com/api/users')
    try:
        users = res.json()
        for user in users:
            print("Username: " + user['username'] + " - " + "ID: " + user['id'])
    except:
        print('No users found')
    return users

# Function get all booking orders of a user through given user ID
def get_user_bookings(userId):
    user_bookings = []
    res = requests.get('https://my-project-1551900810701.df.r.appspot.com/api/bookings')
    try:
        bookings = res.json()
        for booking in bookings:
            if booking['userId'] == str(userId):
                user_bookings.append(booking)
                print("Booking ID: " + booking['id'] + " - " + "User ID: " + booking['userId'] + " - " + "Car ID: " + booking['carId'])
    except:
        print('User has no booking order')
    return user_bookings

# Function return detail of a car that is booked by user through given booking ID
def get_user_booked_car(bookingId):
    booked_car = {}
    booking = {}
    # Get user's booking detail through given booking ID
    res = requests.get('https://my-project-1551900810701.df.r.appspot.com/api/bookings/' + str(bookingId))
    try:
        # Booking detail
        booking = res.json()
        # Get user's booked car detail through the carId given in the booking detail
        res_1 = requests.get('https://my-project-1551900810701.df.r.appspot.com/api/cars/' + booking['carId'])
        # User's booked car detail
        booked_car = res_1.json()
        print('Car ID: ' + booked_car['id'] + " - " + "Car Make: " + booked_car['make'])
    except:
        print("User has no booking order")
    return booked_car

# Function to change carStatus of a car through given carId and given status value
def update_carStatus(carId, new_status):
    res = requests.get('https://my-project-1551900810701.df.r.appspot.com/api/cars/' + carId)
    try: 
        car = res.json()
        update_data = {
            "id": car['id'],
            "carCode": car['carCode'],
            "make": car['make'],
            "carName": car['carName'],
            "bodyType": car['bodyType'],
            "colour": car['colour'],
            "seats": car['seats'],
            "carLocation": car['carLocation'],
            "costPerHour": car['costPerHour'],
            "carStatus": new_status,
            "carImage": car['carImage']
        }
        # Update car with new status
        r = requests.put('https://my-project-1551900810701.df.r.appspot.com/api/cars/', data = update_data)
        print("Update car with new status successfully")
    except:
        print("Can't update car with new status")

def verify_user():
    authenticated_user={}
    while True:
        # Display all users
        print("")
        print("<------------Display All Users-------------->")
        get_users()
        print("<------------------------------------------->")
        print("")

        # Collect user inputs
        print("Please choose one of the login options below:")
        print("[1] Login with your username")
        print("[2] Login with your google account")
        choice = input("Enter your choice [1,2]: ")    
        
        # Login via username and pwd
        if choice == "1":
            username = input("Enter username: ")
            print("Username is: " + username)
            password_candidate = getpass()

            try:
                imported_users = requests.get('https://my-project-1551900810701.df.r.appspot.com/api/users')
                users = imported_users.json()
                for user in users:
                    if user['id'][0:len(username)] == username:
                        stored_password = user['pwd']
                        salt = user['salt']
                        password_target = password_candidate + salt
                        if sha256_crypt.verify(password_target, stored_password):
                            authenticated_user=user
                            print("Login verified")
                            # pwd = sha256_crypt.encrypt(str(passSalt))
            except:
                print("Invalid Login")

        # Login via google account
        elif choice == "2":
            gmail = input("Enter email address: ")
            print("Email is: " + gmail)
            try:
                no_user = True
                imported_users = requests.get('https://my-project-1551900810701.df.r.appspot.com/api/users')
                users = imported_users.json()
                for user in users:
                    if user['gmail'] == gmail:
                        authenticated_user=user
                        no_user = False
                        print("Login verified")

                if no_user == True:
                    print("No user with email found")
            except:
                print("Invalid Login")
        else: print("Invalid choice input")

        # Check if user possessed a folder to be used for facial recognition
        if bool(authenticated_user) == False:
            print("No valid user")
        elif bool(authenticated_user) == True:
            username_1 = authenticated_user['username']
            id_1 = authenticated_user['id']
            safe_file_name = str(id_1).replace(' ', '_')
            path_bool = os.path.exists("/home/pi/AgentPiConnector/images_folder/%s" % safe_file_name)
            print(path_bool)
            if path_bool == True:
                print("Your facial recognition was registered")
            else:
                # Create a folder to store user image if folder not existed. Folder will be named as '<username>-<id>'
                
                choice_2 = input("Do you want to register for facial recognition? (y/n):")
                if choice_2.lower() == "y":
  
                    # Directory Name ('<user_id>')
                    directory = id_1
                    
                    # Parent Directory path 
                    parent_dir = "/home/pi/AgentPiConnector/images_folder/"
                    
                    safe_name = directory.replace(' ', '_')

                    # Path 
                    path = os.path.join(parent_dir, safe_name)
                    print(path)
                    
                    # Create the directory 
                    # '<username>-<id>' in '/home/pi/AgentPiConnector/images_folder/' 

                    try:  
                        os.makedirs(path)
                        print("Directory '% s' created" % safe_name)
                    except OSError as error:  
                        print(error)

            # Display all user's booking orders
            print("----------------------------------")
            print("Display all user's booking orders:")
            get_user_bookings(authenticated_user['id'])
            print("----------------------------------")

            choice_3 = input("Choose and enter a user's booking ID to view booked car detail: ")
            if choice_3 != "":
                get_user_booked_car(choice_3)
            else: print("Invalid booking ID")
                    
# Execute Program
verify_user()