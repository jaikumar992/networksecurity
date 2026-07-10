import sys
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,DataValidationConfig
)

if __name__ == "__main__":
    try:
        # Create Training Pipeline Config
        training_pipeline_config = TrainingPipelineConfig()

        # Data ingestion
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        logging.info("Initiating Data Ingestion")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed")
        print(data_ingestion_artifact)

        # Data validation
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
        logging.info("Data validation initiate")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation complete")

    except Exception as e:
        raise NetworkSecurityException(e, sys)