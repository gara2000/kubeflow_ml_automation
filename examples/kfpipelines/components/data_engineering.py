from kfp import dsl
from kfp.dsl import Input, Output, Dataset

@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2'])
def create_dataset(iris_dataset: Output[Dataset]):
    import pandas as pd
    from sklearn.datasets import load_iris

    csv_url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data'
    col_names = [
        'Sepal_Length', 'Sepal_Width', 'Petal_Length', 'Petal_Width', 'Labels'
    ]
    df = pd.read_csv(csv_url, names=col_names)

    # iris = load_iris()
    # df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    # df['Labels'] = iris.target
    
    print("Dataset columns:", df.columns)
    with open(iris_dataset.path, 'w') as f:
        df.to_csv(f, index=False)


@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2'])
def normalize_dataset(
    input_iris_dataset: Input[Dataset],
    normalized_iris_dataset: Output[Dataset],
    standard_scaler: bool,
    min_max_scaler: bool,
):
    if standard_scaler is min_max_scaler:
        raise ValueError(
            'Exactly one of standard_scaler or min_max_scaler must be True.')

    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.preprocessing import StandardScaler

    with open(input_iris_dataset.path) as f:
        df = pd.read_csv(f)
    labels = df.pop('Labels')

    if standard_scaler:
        scaler = StandardScaler()
    if min_max_scaler:
        scaler = MinMaxScaler()

    df = pd.DataFrame(scaler.fit_transform(df))
    df['Labels'] = labels
    with open(normalized_iris_dataset.path, 'w') as f:
        df.to_csv(f, index=False)
