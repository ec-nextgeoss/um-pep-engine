#!/usr/bin/env python3
import pymongo

class Mongo_Handler:

    def __init__(self, **kwargs):
        self.modified = []
        self.__dict__.update(kwargs)
        self.myclient = pymongo.MongoClient('localhost', 27017)
        self.db = self.myclient["resource_db"]

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
            found=col.find_one(myquery)
            if found:
                k.append(found['resource_id'])   
        return k[-1]

    def resource_exists(self, resource_id):
        '''
            Check the existence of the resource inside the database
            Return boolean result
        '''
        col = self.db['resources']  
        myquery = { "resource_id": resource_id }
        if col.find_one(myquery): return True
        else: return False

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
        dblist = self.myclient.list_database_names()
        # Check if the database alredy exists
        if "resource_db" in dblist:
            col = self.db['resources']
            # Check if the resource is alredy registered in the collection
            if self.resource_exists(resource_id):
                return None
            # Add the resource since it doesn't exist on the database 
            myres = { "resource_id": resource_id, "name": name, "reverse_match_url": reverse_match_url }
            x = col.insert_one(myres)
            return x
        else:
            col = self.db['resources']
            myres = { "resource_id": resource_id, "name": name, "reverse_match_url": reverse_match_url }
            x = col.insert_one(myres)
            return x

        

    def delete_resource(self, resource_id):
        '''
            Check the existence of the resource inside the database
            And deletes the document
        '''
        if self.resource_exists(resource_id):
            col = self.db['resources']  
            myquery = { "resource_id": resource_id }
            a= col.delete_one(myquery)
