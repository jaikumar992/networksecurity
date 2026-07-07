import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
)

if __name__ == "__main__":
    try:
        # Create Training Pipeline Config
        training_pipeline_config = TrainingPipelineConfig()

        # Create Data Ingestion Config
        data_ingestion_config = DataIngestionConfig(
            training_pipeline_config=training_pipeline_config
        )

        # Create Data Ingestion Object
        data_ingestion = DataIngestion(data_ingestion_config)

        logging.info("Initiating Data Ingestion")

        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()

        print(data_ingestion_artifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)