### REFERENCE: https://www.w3schools.com/python/python_dictionaries.asp

import requests
import os
from passlib.hash import sha256_crypt
import json

# Create a class
class bookingHandler:
    @classmethod
    def show_booking(cls, userId):
        # Function get all booking orders of a user through given user ID
        
        user_bookings = []
        res = requests.get('http://carshare-289209.df.r.appspot.com/api/bookings')
        try:
            bookings = res.json()
            for booking in bookings:
                if booking['userId'] == str(userId):
                    booking_dictionary = {
                        "booking_id": booking['id'],
                        "booking_car_id": booking['carId'],
                        "booking_date": booking['bookingDate'],
                        "booking_from": booking['timeFrom'],
                        "booking_duration": booking['nOHours']
                    }
                    user_bookings.append(booking_dictionary)
        except:
            print('User has no booking order')
        return user_bookings

    
    @classmethod
    def get_user_booked_car(cls,carId):
        # Get user's booking detail through given booking ID
        res = requests.get('http://carshare-289209.df.r.appspot.com/api/cars/' + carId)
        try:
            # Booking detail
            car = res.json()
            booked_car_dictionary = {
                "car_id": car['id'],
                "car_brand": car['make'],
                "car_name": car['carName'],
                "car_image": car['carImage']
            }
        except:
            print("User has no booking order")
        return booked_car_dictionary