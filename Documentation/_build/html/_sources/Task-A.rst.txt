Task A
=======

I - How to run car sharing system web application built for customers

First steps:

- Create a project in google cloud platform using your own google account

- Create a sql instance, make sure to provide password to root default user, then create a database named "car_sharing_system"

- We will use Chrome MYSQL Admin browser app to make connection to our created database

  + First, from your google cloud SQL instance page, go to Connections, in Connectivity, select Public IP, then Add network, inside Add network,
  give a name and the ip address of your pc (you can google "my ip" to obtain your ip address), once Done, make sure to hit Save and check if your new
  network is added

  + Then, open Chrome MYSQL Admin, also, open Overview in your cloud SQL instance, fill Name with Connection name in Overview, fill Host name with
  Public IP address in Overview, Port no. is 3306, User name is root, Password is the one you set earlier above

  + Connect and access your car_sharing_system database, you can save your connection with Add as favorite

  + Find and choose Query option in the top menu bar, then enter these queries to create tables:

  CREATE TABLE users ( 
    id VARCHAR(36), 
    username VARCHAR(30),
    firstname VARCHAR(30),
    lastname VARCHAR(30), 
    pwd VARCHAR(255), 
    salt VARCHAR(16), 
    gmail VARCHAR(50), 
    userType VARCHAR(8),
    macAd VARCHAR(17),
    gg_id VARCHAR(100),
    PRIMARY KEY (id),
    UNIQUE (username)
);
CREATE TABLE cars (
    id VARCHAR(36),
    carCode VARCHAR(6),
    make VARCHAR(30),
    carName VARCHAR(100),
    bodyType VARCHAR(10),
    colour VARCHAR(20),
    seats INTEGER,
    carLocation VARCHAR(50),
    costPerHour INTEGER,
    carStatus VARCHAR(15),
    carImage VARCHAR(255),
    PRIMARY KEY (id)
);
CREATE TABLE bookings (
    id VARCHAR(36),
    cid VARCHAR(255),
    eid VARCHAR(255),
    userId VARCHAR(36),
    carId VARCHAR(36),
    bookingDate VARCHAR(10),
    timeFrom VARCHAR(5),
    nOHours INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (userId) REFERENCES users(id),
    FOREIGN KEY (carId) REFERENCES cars(id)
);
CREATE TABLE issues (
    id VARCHAR(36),
    carId varchar(36),
    issueDetail varchar(50),
    longitude FLOAT,
    latitude FLOAT,
    timeNdate VARCHAR(19),
    issueStatus VARCHAR(10)
);

  + Execute and you can view your created tables now

- Next, follow this guide to obtain your own Client ID and Client Secret Key from GCP: https://developers.google.com/identity/sign-in/web/sign-in, 
  only complete the steps provided in Create authorization credentials section:
  + Remember, in the Credentials section of OAuth 2.0 Client IDs of your webapp, make sure to edit Authorized JavaScript origins and
    Authorized redirect URIs:
    . Authorized JavaScript origins: https://<your_project_id>.df.r.appspot.com --> your_google_app_url
    . Authorized redirect URIs: 
    https://<your_project_id>.df.r.appspot.com/oauth2callback, 
    https://<your_project_id>.df.r.appspot.com/login/google/authorized,
    https://<your_project_id>.df.r.appspot.com/dashboard --> basically, when your login is authorized, you will be redirected to the dashboard of your webapp

- After that, open and edit app.yaml file of this project, you should be able to fill all the config variables with your own obtained cresidentials
  relating to your cloud SQL instance, Client ID and Client Secret Key from GCP, also SECRET_KEY can be defined by yourself

- Let's deploy your app to GCP, before that, make sure you already created a project in GCP, also, you need to install google cloud sdk to use
  its shell to execute the command "gcloud app deploy" for deploying your app. Before running "gcloud app deploy", you can preset which project
  will be your deployment destination, by running this cmd "gcloud config set project MY-PROJECT-ID".

- After deployment, you can use the app via project url, you can get the url from your App Engine dashboard

- Finally, for using REST api, please use Postman and follow the url specified in the code

- Overall REST request urls:
  + GET, POST, PUT: <your_google_app_url>/api/<table_name>/
  + GET BY ID, DELETE: <your_google_app_url>/api/<table_name>/<record_id>
  + For POST, PUT requests, please first edit the Headers in Postman tool as follow:
    . Accept : application/json
    . Content-Type : application/json
    . Prepare JSON Body for POST: {"id": <your_record_id>,"<your_table_column_name>": "<some_value>", ...}
    . Prepare JSON Body for PUT: {"id": <your_record_id> ,"<your_table_column_name>": "<some_value>", ...}

- Final update: in order to enable feature Google App Calendar api, you need to prepare a file named client_secrets.json.
  + This particular file can be downloaded from the OAuth 2.0 Client IDs of your webapp (follow this link: https://console.developers.google.com/apis/credentials) 
    (remember the steps on how to obtain Client ID and Client Secret Key)
  + Remember, in the Credentials section of OAuth 2.0 Client IDs of your webapp, make sure to edit Authorized JavaScript origins and
    Authorized redirect URIs:
    . Authorized JavaScript origins: https://<your_project_id>.df.r.appspot.com --> your_google_app_url
    . Authorized redirect URIs: 
    https://<your_project_id>.df.r.appspot.com/oauth2callback, 
    https://<your_project_id>.df.r.appspot.com/login/google/authorized,
    https://<your_project_id>.df.r.appspot.com/dashboard --> basically, when your login is authorized, you will be redirected to the dashboard of your webapp
  + Make sure to paste your downloaded file into the project directory and rename it as client_secrets.json

- You can try my deployed app through this link: https://carshare-289209.df.r.appspot.com/
- For REST API testing urls:
  + https://carshare-289209.df.r.appspot.com/api/cars
  + https://carshare-289209.df.r.appspot.com/api/users
  + https://carshare-289209.df.r.appspot.com/api/bookings
  + https://carshare-289209.df.r.appspot.com/api/issues
  Remember to follow the REST API guide above to test these urls properly
- For the UI to work and display properly, add 3 entries into the cars table in the database:
  + An entry where bodyType is "Sedan" and make is "category"
  + An entry where bodyType is "SUV" and make is "category"
  + An entry where bodyType is "Minivan" and make is "category"
  Be sure to include the image url for each entry. Every other car entry should have an image url too.

II - How to run unit test for task A

Unit test for task A. Change the URLs in the script according to your deployment URL.

Install Pytest via pip. Using a virtual environment is encouraged.

Use command 'pytest unitTestTaskA.py' to run the test. Your app should pass all 20 tests.

III - AgentPiConnector

AgentPiConnector contains a script which will be used on Agent Pi machine to allow users to login using their registered account done through customer wep application.

Once users inputted their credentials, the script will verify user's credentials and generate a folder containing user's images if the user agreed to register for facial recognition.

The folder containing user's images will be named after the user's id and the images stored in the folder will later be used for facial recognition.
