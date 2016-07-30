#!/usr/bin/env python

"""
sws.py
Simple Web RESTFul Webserver
see README.md
"""

import argparse
from bottle import run, get, post, request
from bson import ObjectId
import json
import sys

from settings import app_settings as settings
from mongo_helper import csvToCollection, getMany, getOne, insertOne


class JSONEncoder(json.JSONEncoder):
    """Needed if we want to return Mongo ObjectId as string in json
    """
    def default(self, oid):
        if isinstance(oid, ObjectId):
            return str(oid)
        return json.JSONEncoder.default(self, oid)


@get('/v1/states/<state>/cities/')
def getCitiesByState(state):
    """
    Returns a json dict containing cities filtered
    by the <state> parameter in the url.
    Can limit results with passing limit and skip
    which corrospond to Mongo find skip and limit
    """
    limit = request.query.get('limit')
    skip = request.query.get('skip')
    cities = getMany("cities", {"state": state}, skip=skip, limit=limit)
    return JSONEncoder().encode(list(cities))


@get('/v1/states/<state>/cities/<city>/')
def getCitiesWithinRadius(state, city):
    """
    Returns a json dict containing cities filtered
    by the <state> within the specified radius (in miles).
    If no radius passed defaults to global radius.
    Can limit results with passing limit and skip
    which corrospond to Mongo find skip and limit
    """
    limit = request.query.get('limit')
    skip = request.query.get('skip')

    radius = 3963.2
    try:
        radius = float(request.query.get("radius"))
    except ValueError:
        return json.dumps({"error": "Incorrect Radius Value"})

    city = getOne("cities", {"name": city, "state": state})
    if not city:
        return "[]"

    cities = getMany("cities",
                    {"loc": {"$geoWithin":
                            {"$centerSphere": [city["loc"], radius/3963.2]}}},
                     skip=skip,
                     limit=limit)

    return JSONEncoder().encode(list(cities))


@get('/v1/users/<user>/visits/')
def getVisitsByUser(user):
    """
    Returns a json dict containing Visits filtered
    by the <user> parameter in the url.
    Can limit results with passing limit and skip
    which corrospond to Mongo find skip and limit
    """
    limit = request.query.get('limit')
    skip = request.query.get('skip')
    visits = getMany("visits", {"user": int(user)}, limit=limit, skip=skip)
    return JSONEncoder().encode(list(visits))


@post('/v1/users/<user>/visits/')
def insertVisitsByUser(user):
    """
    Takes user id url parameter.  Finds user and city passed in form data.
    Adds city state and user id to visits table.
    Returns Ok for success.
    """
    formCity = request.forms.get('city')
    formState = request.forms.get('state')

    city = getOne("cities", {"name": formCity, "state": formState})
    if city is None:
        return json.dumps({"error": "City does not exist"})

    user = getOne("users", {"id": int(user)})
    if user is None:
        return json.dumps({"error": "User does not exist"})

    insertOne("visits", {"city": city["id"],
                         "state": city["name"],
                         "user": user["id"]})

    return json.dumps({"response": "OK"})


def csvImport(filename, collection):
    """
    When executing with the --load argument we attempt
    to load csv data into the appropriate Mongo collection.
    """
    csvToCollection(filename, collection)


def runServer():
    """Runs the Web Server
    """
    run(host=settings["host"], port=settings["port"], debug=True)


def main():
    parser = argparse.ArgumentParser(description="SCC RESTful Web Service")
    parser.add_argument('-f', '--file', help="CSV filename to be loaded into Mongo Collection", type=str)
    parser.add_argument('-c', '--collection', help="Name of Mongo Collection", type=str)
    parser.add_argument('-r', '--run', help="Run the Web Server", action="store_true")
    args = parser.parse_args()

    if args.run:
        runServer()

    if args.file and args.collection:
        csvImport(args.file, args.collection)

    if (args.file and not args.collection) or (args.collection and not args.file):
        print "Error: Need to pass --collection with --file"


if __name__ == "__main__":
    main()
