#!/usr/bin/env python
"""
sws unit tests.
"""

from bottle import request, run, post, tob
from contextlib import contextmanager
from io import BytesIO
import mock

import sws
import mongo_helper


body = "abc"
request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
request.environ['wsgi.input'] = BytesIO()
request.environ['wsgi.input'].write(tob(body))
request.environ['wsgi.input'].seek(0)


def test_getCitiesByState():
    getManyMock = mock.Mock(return_value={})
    sws.getMany = getManyMock
    result = sws.getCitiesByState("IL")
    getManyMock.assert_called_with('cities', {'state': 'IL'}, limit=None, skip=None)
    getManyMock.reset_mock()
    assert result == "[]"


def test_getCitiesByStateWithSkipLimit():
    getManyMock = mock.Mock(return_value={})
    sws.getMany = getManyMock
    sws.request.query["limit"] = 100
    sws.request.query["skip"] = 20
    result = sws.getCitiesByState("NY")
    getManyMock.assert_called_with('cities', {'state': 'NY'}, limit=100, skip=20)
    getManyMock.reset_mock()
    assert result == "[]"


def test_getCitiesWithinRadius():
    getManyMock = mock.Mock(return_value={})
    getOne = mock.Mock(return_value={"id": 1, "loc": [0, 0]})
    sws.getOne = getOne
    sws.getMany = getManyMock
    sws.request.query["limit"] = 20
    sws.request.query["skip"] = 30
    sws.request.query["radius"] = 50
    result = sws.getCitiesWithinRadius("IL", "Chicago")
    getManyMock.assert_called_with('cities', {'loc': {'$geoWithin': {'$centerSphere': [[0, 0], 0.012616067823980621]}}}, limit=20, skip=30)
    getManyMock.reset_mock()
    assert result == "[]"

    
def test_getCitiesWithinRadiusInvalidCity():
    getManyMock = mock.Mock(return_value={})
    getOne = mock.Mock(return_value=None)
    sws.getOne = getOne
    sws.getMany = getManyMock
    sws.request.query["limit"] = 20
    sws.request.query["skip"] = 30
    sws.request.query["radius"] = 50
    result = sws.getCitiesWithinRadius("IL", "Chicago")
    getManyMock.assert_not_called()
    getManyMock.reset_mock()
    assert result == "[]"

    
def test_getVisitsByUser():
    getManyMock = mock.Mock(return_value={})
    sws.getMany = getManyMock
    sws.request.query["limit"] = 40
    sws.request.query["skip"] = 50
    result = sws.getVisitsByUser("1")
    getManyMock.assert_called_with('visits', {'user': 1}, limit=40, skip=50)
    getManyMock.reset_mock()
    assert result == "[]"


def test_insertVisitsByUser():
    sws.request.forms['city'] = 'Seattle'
    sws.request.forms['state'] = 'WA'
    insertOneMock = mock.Mock(return_value={})
    getOne = mock.Mock(return_value={"id": 1, "name": "Seattle", "state": "WA"})
    sws.getOne = getOne
    sws.insertOne = insertOneMock
    result = sws.insertVisitsByUser("1")
    insertOneMock.assert_called_with('visits', {'city': 1, 'state': 'Seattle', 'user': 1})
    insertOneMock.reset_mock()
    assert result == '{"response": "OK"}'


def test_insertVisitsByUserNoCity():
    sws.request.forms['city'] = 'Seattle'
    sws.request.forms['state'] = 'WA'
    insertOneMock = mock.Mock(return_value={})
    getOne = mock.Mock(return_value=None)
    sws.getOne = getOne
    sws.insertOne = insertOneMock
    result = sws.insertVisitsByUser("1")
    insertOneMock.assert_not_called()
    insertOneMock.reset_mock()
    assert result == '{"error": "City does not exist"}'


def test_insertVisitsByUserNoUser():
    sws.request.forms['city'] = 'Seattle'
    sws.request.forms['state'] = 'WA'
    insertOneMock = mock.Mock(return_value=[])
    getOne = mock.Mock()
    getOne.side_effect = [True, None]
    sws.getOne = getOne
    sws.insertOne = insertOneMock
    result = sws.insertVisitsByUser("1")
    insertOneMock.assert_not_called()
    insertOneMock.reset_mock()
    assert result == '{"error": "User does not exist"}'


def test_mongoAddCollectionIdIndex():
    collectionMock = mock.Mock(return_value={})
    createIndexMock = mock.Mock()
    setattr(mongo_helper.db, "collection", collectionMock)
    getattr(mongo_helper.db, "collection").create_index = createIndexMock
    mongo_helper.addCollectionIdIndex("collection")
    createIndexMock.assert_called_with('id', unique=True)
    createIndexMock.reset_mock()


def test_mongoinsertOne():
    collectionMock = mock.Mock(return_value={})
    insertOneMock = mock.Mock()
    setattr(mongo_helper.db, "collection", collectionMock)
    getattr(mongo_helper.db, "collection").insert_one = insertOneMock
    mongo_helper.insertOne("collection", "record")
    insertOneMock.assert_called_with("record")
    insertOneMock.reset_mock()


def test_getOne():
    collectionMock = mock.Mock(return_value={})
    getOneMock = mock.Mock()
    setattr(mongo_helper.db, "collection", collectionMock)
    getattr(mongo_helper.db, "collection").find_one = getOneMock
    mongo_helper.getOne("collection", "record")
    getOneMock.assert_called_with("record", None)
    getOneMock.reset_mock()


def test_getMany():
    class Limit(object):
        def limit(self, limit):
            return 10
    collectionMock = mock.Mock(return_value={})
    getManyMock = mock.Mock(return_value=Limit())
    setattr(mongo_helper.db, "collection", collectionMock)
    getattr(mongo_helper.db, "collection").find = getManyMock
    result = mongo_helper.getMany("collection", "record", "items")
    getManyMock.assert_called_with("record", "items")
    getManyMock.reset_mock()
    assert result == 10


def test_getManySkip():
    class Limit(object):
        def limit(self, limit):
            return 20
    class Skip(object):
        def skip(self, limit):
            return Limit()
    collectionMock = mock.Mock(return_value={})
    getManyMock = mock.Mock(return_value=Skip())
    setattr(mongo_helper.db, "collection", collectionMock)
    getattr(mongo_helper.db, "collection").find = getManyMock
    result = mongo_helper.getMany("collection", "record", "items", skip=10, limit=100)
    getManyMock.assert_called_with("record", "items")
    getManyMock.reset_mock()
    assert result == 20


def test_csvToCollection():
    @contextmanager
    def openMockManager():
        yield []
    openMock = mock.Mock(return_value=openMockManager())
    mongo_helper.open = openMock
    dictReaderMock = mock.Mock(return_value=[{"id": 1}])
    mongo_helper.csv.DictReader = dictReaderMock
    collectionMock = mock.Mock(return_value=[])
    insertMock = mock.Mock()
    setattr(mongo_helper.db, "collection", collectionMock)
    getattr(mongo_helper.db, "collection").insert = insertMock
    mongo_helper.csvToCollection("file", "collection")
    insertMock.assert_called_with({"id": 1})
    insertMock.reset_mock()
