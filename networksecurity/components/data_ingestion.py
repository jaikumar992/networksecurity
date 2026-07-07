from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifacts

import os
import sys
import pymongo
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
import certifi


class DataIngestion:

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self):
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            try:
                self.mongo_client = pymongo.MongoClient(
                    MONGO_DB_URL,
                    tls=True,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=30000
                )

                # Force server selection / TLS handshake now so failures raise here
                self.mongo_client.admin.command('ping')

                collection = self.mongo_client[database_name][collection_name]

                df = pd.DataFrame(list(collection.find()))
            except Exception as mongo_exc:
                logging.warning(f"MongoDB connection failed: {mongo_exc}. Trying local CSV fallback.")

                # Attempt to load local CSV fallback from project root
                local_csv = os.path.join(os.getcwd(), "Network_Data", "phisingData.csv")
                if os.path.exists(local_csv):
                    df = pd.read_csv(local_csv)
                else:
                    # re-raise the original Mongo error wrapped
                    raise mongo_exc

            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"], axis=1, inplace=True)

            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = (
                self.data_ingestion_config.feature_store_file_path
            )

            dir_path = os.path.dirname(feature_store_file_path)

            os.makedirs(dir_path, exist_ok=True)

            dataframe.to_csv(
                feature_store_file_path,
                index=False,
                header=True
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio
            )

            logging.info("Performed train test split on the dataframe")

            dir_path = os.path.dirname(
                self.data_ingestion_config.training_file_path
            )

            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(
                self.data_ingestion_config.training_file_path,
                index=False,
                header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,
                index=False,
                header=True
            )

            logging.info("Train and test files exported successfully.")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()

            dataframe = self.export_data_into_feature_store(dataframe)

            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifacts(
                trained_file_path=self.data_ingestion_config.training_file_path,
                testing_file_path=self.data_ingestion_config.testing_file_path
            )

            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)