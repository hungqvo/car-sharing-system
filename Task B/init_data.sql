CREATE TABLE users ( 
    id VARCHAR(36), 
    username VARCHAR(30),
    firstname VARCHAR(30),
    lastname VARCHAR(30), 
    pwd VARCHAR(64), 
    salt VARCHAR(16), 
    gmail VARCHAR(50), 
    userType VARCHAR(8),
    macAd VARCHAR(17),
    UNIQUE (username),
    PRIMARY KEY (id)
);
CREATE TABLE cars (
    id VARCHAR(36),
    carCode VARCHAR(6),
    make VARCHAR(30),
    bodyType VARCHAR(10),
    colour VARCHAR(20),
    seats INTEGER,
    carLocation VARCHAR(50),
    costPerHour INTEGER,
    carStatus VARCHAR(15), 
    PRIMARY KEY (id)
);
CREATE TABLE bookings (
    id VARCHAR(36),
    userId VARCHAR(36),
    carId VARCHAR(36),
    bookingDate VARCHAR(10),
    timeFrom VARCHAR(5),
    timeTo VARCHAR(5),
    nOHours INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (userId) REFERENCES users(id),
    FOREIGN KEY (carId) REFERENCES cars(id)
    ON DELETE CASCADE

);
CREATE TABLE issues (
    id VARCHAR(36),
    carId varchar(36),
    issueDetail varchar(50),
    longitude FLOAT,
    latitude FLOAT,
    timeNdate VARCHAR(19),
    issueStatus VARCHAR(10),
    PRIMARY KEY (id),
    FOREIGN KEY (carId) REFERENCES cars(id)
    ON DELETE CASCADE
);
 INSERT INTO users (id, username, firstname, lastname, pwd, salt, gmail, userType, macAd) VALUES 
 (uuid(), 
 "admin1",
 "admin",
 "admin", 
 "5bf17befd480ddf3e775502d45170dc48f1a6793104d23448aacb002ff1e0a84", 
 "77aa3edd22766057",
 "khanhniii07@gmail.com",
 "engineer",
 "20:47:da:b6:59:7b"
 );
 INSERT INTO users (id, username, firstname, lastname, pwd, salt, gmail, userType, macAd) VALUES 
 (uuid(), 
 "user1",
 "Sam",
 "H", 
 "5bf17befd480ddf3e775502d45170dc48f1a6793104d23448aacb002ff1e0a84", 
 "77aa3edd22766057",
 "khanhniii07@gmail.com",
 "user",
 "thisisseco"
 );

 INSERT INTO cars (id, carCode, make, bodyType, colour, seats, carLocation, costPerHour, carStatus) VALUES
 (uuid(),
 "HD82Y7",
 "BMW",
 "Hasback",
 "Grey",
 4,
 "RMIT VN",
 30,
 "available"
 );
 INSERT INTO cars (id, carCode, make, bodyType, colour, seats, carLocation, costPerHour, carStatus) VALUES
 (uuid(),
 "FUL9U9",
 "Toyota",
 "Hasback",
 "Grey",
 4,
 "LotteMart",
 17,
 "booked"
 );

 INSERT INTO bookings (id, userId, carId, bookingDate, timeFrom, timeTo, nOHours) VALUES 
 (uuid(),
 "fa88c51e-f3e7-11ea-8730-0242ac130002",
 "79a5a9e2-f3d6-11ea-8730-0242ac130002",
 "2020-08-16",
 "11:00",
 "15:00",
 4
 );
 INSERT INTO bookings (id, userId, carId, bookingDate, timeFrom, timeTo, nOHours) VALUES 
 (uuid(),
 "3f78ae9a-fa1a-11ea-aa9d-0242ac1a0002",
 "f949956d-fa19-11ea-aa9d-0242ac1a0002",
 "2020-08-16",
 "9:00",
 "18:00",
 9
 );


