import os

import fasttext
import mlflow


remote_server_uri = "http://35.225.84.215"
mlflow.set_tracking_uri(remote_server_uri)
# Note: on Databricks, the experiment name passed to mlflow_set_experiment must be a
# valid path in the workspace
mlflow.set_experiment("training-fasttext-embeddings")
with mlflow.start_run():
    mlflow.log_param("USER", os.environ.get('HOME', '/home/None').split('/')[-1])

    file_path = 'sci.space.txt'
    model_path = 'skipgram.model'
    model = fasttext.train_unsupervised(file_path, model='skipgram', dim=3, bucket=1000)
    model.save_model(model_path)

    mlflow.log_artifact(model_path)
