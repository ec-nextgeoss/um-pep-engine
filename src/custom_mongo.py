#!/usr/bin/env python3
import pymongo

class Mongo_Handler:

    def __init__(self, **kwargs):
        self.modified = []
        self.__dict__.update(kwargs)
        self.myclient = pymongo.MongoClient('localhost', 27017)
        self.db = self.myclient["resource_db"]

    # def get_id_from_uri(self, uri):
    #     col = self.db['resources']
    #     res = []
    #     col.create_index([("reverse_match_url", pymongo.TEXT)])
    #     for x in col.find({'$text': {'$search': str(uri) }},{ 'score': {'$meta': "textScore"}}).sort([('score', {'$meta': "textScore"})]):
    #         if x and len(x['reverse_match_url'])<=len(uri): res.append(x)
    #     x = None
    #     if len(res) != 0:
    #         print(res)
    #     else: 
    #         x =str(col.find({'reverse_match_url' : '/'}))
    #     if not x: return None

    def get_id_from_uri(self,uri):
        '''
            Finds the most similar match with the uri given
            Generates a list of the possible matches
            Returns resource_id of the best match

        '''
        total= '/'
        col= self.db['resources']
        k=[]
        uri_split=uri.split('/')
        count=0
        for n in uri_split:
            if count >= 2:
                total = total + '/' + n
            else:
                total = total + n
            count+=1
            myquery = { "reverse_match_url": total }
            for l in col.find(myquery):
                k.append(l['resource_id'])   
        return k[-1]

    def resource_exists(self, resource_id):
        '''
            Check the existence of the resource inside the database
            Return boolean result
        '''
        col = self.db['resources']  
        myquery = { "resource_id": resource_id }
        for x in col.find(myquery):
            if x: return True
        return False

    def insert_in_mongo(self, resource_id: str, name: str, reverse_match_url: str):   
        '''
            Generates a document with:
                -RESOURCE_ID: Unique id for each resource
                -RESOURCE_NAME: Custom name for the resource (NO restrictions)
                -RESOURCE_URL: Stored endpoint for each resource
            Check the existence of the resource to be registered on the database
            If alredy registered will return None
            If not registered will add it and return the query result
        '''
        col = None
        dblist = self.myclient.list_database_names()
        # Check if the database alredy exists
        if "resource_db" in dblist:
            col = self.db['resources']
            # Check if the resource is alredy registered in the collection
            for x in col.find({},{ "_id": 0, "resource_id": 1, }):
                if resource_id in str(x):
                    print('Resource alredy registered in the database')
                    return None
            # Add the resource since it doesn't exist on the database 
            myres = { "resource_id": resource_id, "name": name, "reverse_match_url": reverse_match_url }
            x = col.insert_one(myres)
            return x
        else:
            # In case the database doesn't exist it will create it with the resource
            col = db['resources']
            myres = { "resource_id": resource_id, "name": name, "reverse_match_url": reverse_match_url }
            x = col.insert_one(myres)
            return x

# mongo = Mongo_Handler()
# mongo.insert_in_mongo('a123','re1','/pep/ADES')
# mongo.insert_in_mongo('b234','re2','/pep')
# mongo.insert_in_mongo('c345','re3','/mongo/test/y')
# mongo.insert_in_mongo('d456','re4','/pep/ADES/som')
# mongo.insert_in_mongo('e567','re5','/pep/ADES/som/3')
# mongo.insert_in_mongo('f678','re6','/')
# print(mongo.resource_exists('f678'))
# print(mongo.get_id_from_uri('/pep/ADES/alg'))
# print(mongo.get_id_from_uri('/jjuanjo/ADES/som'))
# print(mongo.get_id_from_uri('/mongo/test'))
# print(mongo.get_id_from_uri('/mongo/test/y/alvl/test'))
# print(mongo.get_id_from_uri('/pep/ADES/som'))
