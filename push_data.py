import sys 
import os
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")

import pandas as pd
import numpy as np
import pymongo 
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

import certifi 
ca=certifi.where()

class NetworkDataExtraction():
    def __init__(self):
        try:
           pass
        except Exception as e:
           raise NetworkSecurityException(e,sys)
    
    def csv_to_json_converter(self,file_path):
        try:
            data=pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)
            record=list(json.loads(data.T.to_json()).values())
            return record
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def insert_data_mongodb(self,record,database,collection):
        try:
            self.record=record
            self.database=database
            self.collection=collection

            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            self.database=self.mongo_client[self.database]

            self.collection=self.database[self.collection]
            self.collection.insert_many(self.record)
            return(len(self.record))
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
if __name__ =="__main__":
    FILE_PATH="Network_Data\phisingData.csv"
    DATABASE="jaikumar"
    Collection="NetworkData"
    networkobj=NetworkDataExtraction()
    records=networkobj.csv_to_json_converter(file_path=FILE_PATH)
    print(records)
    no_of_records=networkobj.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)



    
    

    
     

