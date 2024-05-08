import sys
from dataclasses import dataclass

import numpy as np 
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

from src.exception import CustomException
from src.logger import logging
import os

from src.utils import save_obj

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts', 'preprocessed.pkl')
    
class DataTransformation:
    
    """
    This class transforms data (Imputation, One-hot-encoding, Standard Scaler)
    """
    
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()
        
    def get_data_transformer_obj(self):
        
        try:
            numerical_columns = ['HorsePower', 'kilometer']
            categorical_columns = ['Seller', 'offerType', 'abtest', 'vehicleType', 'gearbox', 'fuelType', 'NotRepaired/Damaged','Risk_Level']
            
            num_pipeline = Pipeline(
                steps = [
                    ('imputer', SimpleImputer(strategy='median')),
                     ('scaler', StandardScaler())
                ]
            )
            
            cat_pipeline = Pipeline(
                steps = [
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('one_hot_encoder', OneHotEncoder()),
                    ('scaler', StandardScaler(with_mean=False))
                ]
            )
            logging.info("Numerical & Categorical Pipelines created");
            
            preprocessor = ColumnTransformer(
                [
                    ("num_pipeline", num_pipeline, numerical_columns),
                    ('cat_pipeline', cat_pipeline, categorical_columns)
                ]
            )
            
            return preprocessor
        
        except Exception as e:
            raise CustomException(e, sys)
        
    def initiate_data_transformation(self, train_path, test_path):
        
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            
            logging.info("Train and Test data imported")
            logging.info("Starting Preprocessing")

            preprocessing_obj = self.get_data_transformer_obj()
            
            target_col_name = 'Price'
            numerical_columns = ['HorsePower', 'kilometer']
            categorical_columns = ['Seller', 'offerType', 'abtest', 'vehicleType', 'gearbox', 'fuelType', 'NotRepaired/Damaged','Risk_Level']
            
            input_feature_train_df = train_df.drop(columns = [target_col_name], axis=1)
            target_feature_train_df = train_df[target_col_name]
            
            input_feature_test_df = test_df.drop(columns = [target_col_name], axis=1)
            target_feature_test_df = test_df[target_col_name]
            
            logging.info("Applying preprocessing object on training df and testing df.")

            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)
            
            transformed_columns = (
            preprocessing_obj.named_transformers_['num_pipeline'].named_steps['scaler'].get_feature_names_out(numerical_columns).tolist()
            + preprocessing_obj.named_transformers_['cat_pipeline'].named_steps['one_hot_encoder'].get_feature_names_out(categorical_columns).tolist()
            )
            
            dense_input_feature_train_arr = input_feature_train_arr.toarray()
            dense_input_feature_test_arr = input_feature_test_arr.toarray()
            
            # Create DataFrame using dense matrix and column names
            input_feature_train_arr = pd.DataFrame(dense_input_feature_train_arr, columns=transformed_columns)
            input_feature_test_arr = pd.DataFrame(dense_input_feature_test_arr, columns=transformed_columns)
        
            train_arr = pd.concat([input_feature_train_arr, target_feature_train_df], axis=1)            
            test_arr = pd.concat([input_feature_test_arr, target_feature_test_df], axis=1)

            logging.info(f"Saved preprocessing object.")
            
            save_obj(
                file_path = self.data_transformation_config.preprocessor_obj_file_path,
                obj = preprocessing_obj
            )

            return(train_arr, test_arr, self.data_transformation_config.preprocessor_obj_file_path)
            
        except Exception as e:
            raise CustomException(e, sys)