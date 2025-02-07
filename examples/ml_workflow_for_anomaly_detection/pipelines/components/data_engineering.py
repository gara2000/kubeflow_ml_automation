from kfp import dsl
from kfp.dsl import Input, Output, Dataset

@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2'])
def data_extraction(data_path: str, output_data: Output[Dataset]):
    import pandas as pd
    from sklearn.datasets import load_iris

    df = pd.read_csv(data_path)

    with open(output_data.path, 'w') as f:
        df.to_csv(f, index=False)
    
@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2'])
def data_processing(
    train_input: str,
    train_output: str, 
    train_data: Output[Dataset],
    test_data: Output[Dataset]
):
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import MinMaxScaler

    # Load the data
    training_inputs = pd.read_csv(train_input)
    training_outputs = pd.read_csv(train_output)
    training_data = pd.merge(training_outputs, training_inputs, on='PROC_TRACEINFO')

    def processing():
        df_train, df_test = train_test_split(training_data, test_size=0.2, random_state=1)

        X_train = df_train.drop(columns=['PROC_TRACEINFO', 'Binar OP130_Resultat_Global_v'])
        X_test = df_test.drop(columns=['PROC_TRACEINFO', 'Binar OP130_Resultat_Global_v'])

        # Change the column OP100_Capuchon_insertion_mesure to a binary column
        X_train['OP100_Capuchon_insertion_mesure'] = X_train['OP100_Capuchon_insertion_mesure'].isnull()
        X_test['OP100_Capuchon_insertion_mesure'] = X_test['OP100_Capuchon_insertion_mesure'].isnull()

        # Scale the data
        scaler = MinMaxScaler()
        scaler.fit(X_train)

        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test) 

        train_df = pd.DataFrame(X_train)
        test_df = pd.DataFrame(X_test)

        y_train = list(df_train['Binar OP130_Resultat_Global_v'])
        y_test = list(df_test['Binar OP130_Resultat_Global_v'])

        train_df['y'] = y_train
        test_df['y'] = y_test
        return train_df, test_df 

    train_df, test_df = processing()    
    with open(train_data.path, 'w') as f:
        train_df.to_csv(f, index=False)
    with open(test_data.path, 'w') as f:
        test_df.to_csv(f, index=False)

@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2', 'imblearn==0.0'])
def data_resampling(
    train_data: Input[Dataset],
    resampled_data: Output[Dataset],
    oversampling_coeff: int = 1,
    undersampling_coeff: int = 1,
):
  """
  Resample the dataset to balance the classes.

  Parameters:
  - train_data: Training dataset artifact
  - oversampling_coeff: Rate of minority class relative to majority class in oversampling strategy
  - undersampling_coeff: Rate of minority class relative to majority class in undersampling strategy

  Returns:
  - resampled_data: Resampled dataset artifact
  """
  from imblearn.over_sampling import SMOTE
  from imblearn.under_sampling import RandomUnderSampler
  from imblearn.pipeline import Pipeline
  import numpy as np
  import pandas as pd

  oversample = SMOTE(sampling_strategy=oversampling_coeff, random_state=42)  # Oversample minority to 5% of majority
  undersample = RandomUnderSampler(sampling_strategy=undersampling_coeff, random_state=42)  # Undersample majority to 5x minority

  resample_pipeline = Pipeline([
      ('smote', oversample),
      ('undersample', undersample)
  ])

  df_train = pd.read_csv(train_data.path)

  X_train = df_train.drop(columns=["y"])
  y_train = df_train["y"]

  X_resampled, y_resampled = resample_pipeline.fit_resample(X_train, y_train)

  df_resampled = pd.concat([X_resampled, y_resampled], axis=1)

  with open(resampled_data.path, 'w') as f:
    df_resampled.to_csv(f, index=False)
