from dataclasses import dataclass

@dataclass
class DataIngestionArtifacts:
    trained_file_path:str
    testing_file_path:str