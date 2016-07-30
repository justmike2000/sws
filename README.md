Simple Web RESTful Server
======================================

# Description:

    Implements a basic RESTful API Service with the following endpoints:

    1. List all cities in a state

        `GET /v1/states/{state}/cities`

    2. List cities within a 100 mile radius of a city

        `GET /v1/states/{state}/cities/{city}?radius=100`

    3. Allow a user to update a row of data to indicate they have visited a particular city.

        `POST /v1/users/{user}/visits`

        ```
        {
            "city": "Chicago",
            "state": "IL"
        }
        ```

    4. Return a list of cities the user has visited

        `GET /v1/users/{user}/visits`

    5. Each endpoint takes limit and skip parameters which corresponds to Mongo skip and limit. (Defaults 1000 Limit)


# External Dependencies:

    * Python2.7.x
    * MongoDB 2.4

# Installation:

    **It is recommended to use Python Virtualenv**
    **http://virtualenv.readthedocs.org/en/latest/**
    ** requirments.txt For standard execution
    ** requirments-test.txt for test
    pip install -r requirements.txt

# Settings:

    A settings.cfg has been provided for you to configure Web Server and MongoDB settings.

# Importing Data:
    python sws.py --file cities.csv --collection cities
    python sws.py --file users.csv --collection users

# Run:
    python sws.py --run


# Tests:
    nosestests
