import smtplib, ssl

port = 465  # For SSL
password = input("Type your password and press enter: ")

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login("khanhniii07@gmail.com", password)
    server.sendmail("khanhniii07@gmail.com", "crycuronly@gmail.com", "hello receiver")