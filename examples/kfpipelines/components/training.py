from kfp import dsl
from kfp.dsl import Input, Dataset, Output, Model, Metrics

@dsl.component(
    packages_to_install=['scikit-learn==1.5.2', 'joblib==1.4.2', 'pandas==2.2.3', 'numpy==2.0.2', 'docker==7.1.0', 'kubernetes==31.0.0', 'gitpython==3.1.43']
)
def train_model(
    model: Output[Model],
    data: Input[Dataset],
    metrics: Output[Metrics],  # Metrics artifact
):
    import joblib
    import pickle
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score

    # Load the dataset
    df = pd.read_csv(data.path)
    y = df.pop('Labels')
    X = df

    # Split into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the classifier
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate the model
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"Accuracy: {accuracy}")
    print(f"F1 Score: {f1}")

    # Save the model to the output path
    # joblib.dump(clf, model.path)
    with open(model.path, "wb") as f:
        pickle.dump(clf, f)

    model_path = model.path
    print(f"Model saved to {model_path}")

    # Log metrics
    metrics.log_metric("accuracy", accuracy)
    metrics.log_metric("f1_score", f1)