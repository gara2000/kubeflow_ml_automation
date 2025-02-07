from typing import List

from kfp import client
from kfp import dsl
from kfp.dsl import Dataset
from kfp.dsl import Input
from kfp.dsl import Model
from kfp.dsl import Output
from kfp import kubernetes



@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2'])
def create_dataset(
    file_prefix: str
):
    import pandas as pd

    csv_url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data'
    col_names = [
        'Sepal_Length', 'Sepal_Width', 'Petal_Length', 'Petal_Width', 'Labels'
    ]
    df = pd.read_csv(csv_url, names=col_names)

    with open(f'/data/{file_prefix}.csv', 'w') as f:
        df.to_csv(f)


@dsl.pipeline(name='pvc_test_pipeline')
def pvc_test_pipeline():
    # pvc1 = kubernetes.CreatePVC(
    #     # can also use pvc_name instead of pvc_name_suffix to use a pre-existing PVC
    #     pvc_name='model-registry-pvc',
    # )
    task1 = create_dataset(file_prefix="task1")
    # task2 = create_dataset(file_prefix="task2").after(task1)

    # kubernetes.mount_pvc(
    #     task2,
    #     pvc_name=pvc1.outputs['name'],
    #     mount_path='/data',
    # )
    kubernetes.mount_pvc(
        task1,
        pvc_name="model-registry-pvc",
        mount_path='/data',
    )
