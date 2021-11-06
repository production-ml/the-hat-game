from google.cloud import storage


def get_storage(project_id):
    """Function to define where game artifacts are stored.
    game_scope could be "GLOBAL" or "LOCAL".
    If game_scope is "GLOBAL", artifacts are stored on the Google server.
    If game_scope is "LOCAL", artifacts are stored locally.
    """
    storage_client = storage.Client(project=project_id)
    return storage_client
