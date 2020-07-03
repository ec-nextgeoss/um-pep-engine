#!/usr/bin/env python3
import pymongo

class Mongo_Handler:

      
    def insert_in_mongo(self, name: str, resource_id: str, icon_uri: str):   
        '''
            Check the existence of the resource to be registered on the database
            If alredy registered will return None
            If not registered will add it and return the query result
        '''
        myclient = pymongo.MongoClient('localhost', 27017)
        db = myclient["resource_db"]
        col = None
        dblist = myclient.list_database_names()
        # Check if the database alredy exists
        if "resource_db" in dblist:
            print("The database exists.")
            col = db['resources']
            # Check if the resource is alredy registered in the collection
            for x in col.find({},{ "_id": 0, "resource_id": 1, "name": 1 }):
                if new_resource_id in str(x):
                    print('Resource alredy registered in the database')
                    return None
            # Add the resource since it doesn't exist on the database 
            myres = { "resource_id": new_resource_id, "name": name, "icon_uri": uri }
            x = col.insert_one(myres)
            return x
        else:
            # In case the database doesn't exist it will create it with the resource
            col = db['resources']
            myres = { "resource_id": new_resource_id, "name": name, "icon_uri": uri }
            x = col.insert_one(myres)
            return x