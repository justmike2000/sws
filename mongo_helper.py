#!/usr/bin/env python

"""
mongo_helper.py
Set of methods to assist in interacting with Mongo.
"""

import pymongo
import csv

from settings import app_settings as settings


client = pymongo.MongoClient(settings['mongo_host'], settings['mongo_port'])
db = client[settings['mongo_name']]


def addCollectionIdIndex(collection):
    """
    Adds indexes to collections to prevent duplicates.
    """
    try:
        getattr(db, collection).create_index("id", unique=True)
    except pymongo.errors.DuplicateKeyError:
        pass


def insertOne(collection, record):
    """
    Takes string collection (Mongo collection), record (dictionary of items)
    and inserts the dict into the Mongo collection.
    """
    getattr(db, collection).insert_one(record)


def getOne(collection, query=None, items=None):
    """
    Takes string collection (Mongo collection), query (Mongo query)
    and items (which if any items you want returned per record).
    Returns single row.
    """
    return getattr(db, collection).find_one(query, items)


def getMany(collection, query=None, items=None, skip=None, limit=1000):
    """
    Takes string collection (Mongo collection), query (Mongo query)
    and items (which if any items you want returned per record).
    Returns dict.
    """
    result = getattr(db, collection).find(query, items)
    if skip is not None:
        result = result.skip(int(skip))
    if limit is not None:
        result = result.limit(int(limit))
    return result


def csvToCollection(csvfile, collection):
    """
    Takes string location of csv file and collection
    in which the data will be loaded.  If data contains
    latitude and longitude information then this location
    if moved under "loc" in a list to be used with Mongo
    geoSpatial queries.
    """
    addCollectionIdIndex(collection)
    with open(csvfile) as csvreader:
        csvData = csv.DictReader(csvreader)
        for row in csvData:
            row['id'] = int(row['id'])
            if "latitude" in row and "longitude" in row:
                row['loc'] = [float(row["latitude"]), float(row["longitude"])]
                row.pop("latitude")
                row.pop("longitude")
            try:
                getattr(db, collection).insert(row)
            except pymongo.errors.DuplicateKeyError:
                pass
