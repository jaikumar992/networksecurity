from networksecurity.entity.artifact_entity import DataIngestionArtifacts, DatavalidationArtifacts
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH
import sys
from scipy.stats import ks_2samp
import pandas as pd
import os
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifacts,
                 data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            # Resolve schema path relative to package directory
            schema_path = os.path.join(os.getcwd(), "networksecurity", SCHEMA_FILE_PATH)
            if not os.path.exists(schema_path):
                # fallback to package-relative path
                schema_path = SCHEMA_FILE_PATH
            self.schema_config = read_yaml_file(schema_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame,
                             threshold: float = 0.05) -> bool:
        try:
            status = True
            report = {}

            numerical_columns = self.schema_config.get("numerical_columns")
            if numerical_columns is None:
                columns_to_check = base_df.columns
            else:
                columns_to_check = numerical_columns

            for column in columns_to_check:
                if column not in base_df.columns or column not in current_df.columns:
                    continue

                d1 = base_df[column].dropna()
                d2 = current_df[column].dropna()

                try:
                    test_result = ks_2samp(d1, d2)
                    pvalue = float(test_result.pvalue)
                except Exception:
                    pvalue = 0.0

                drift_status = pvalue < threshold
                if drift_status:
                    status = False

                report[column] = {
                    "p_value": pvalue,
                    "drift_status": drift_status
                }

            drift_report_file_path = self.data_validation_config.drift_report_file_path
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)

            write_yaml_file(file_path=drift_report_file_path, content=report)

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self.schema_config.get("columns", {}))

            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Data frame has columns: {len(dataframe.columns)}")

            if len(dataframe.columns) == number_of_columns:
                return True

            return False

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DatavalidationArtifacts:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.testing_file_path

            # Read train and test data
            train_dataframe = self.read_data(train_file_path)
            test_dataframe = self.read_data(test_file_path)

            # Validate number of columns
            status = self.validate_number_of_columns(train_dataframe)
            if not status:
                raise Exception("Train dataframe does not contain all required columns.")

            status = self.validate_number_of_columns(test_dataframe)
            if not status:
                raise Exception("Test dataframe does not contain all required columns.")

            # Check dataset drift
            drift_status = self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)

            # Save validated files
            valid_train_path = self.data_validation_config.valid_train_file_path
            valid_test_path = self.data_validation_config.valid_test_file_path

            os.makedirs(os.path.dirname(valid_train_path), exist_ok=True)
            os.makedirs(os.path.dirname(valid_test_path), exist_ok=True)

            train_dataframe.to_csv(valid_train_path, index=False, header=True)
            test_dataframe.to_csv(valid_test_path, index=False, header=True)

            data_validation_artifact = DatavalidationArtifacts(
                Validation_status=drift_status,
                valid_train_file_path=valid_train_path,
                valid_test_file_path=valid_test_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
    