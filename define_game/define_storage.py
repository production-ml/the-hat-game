from google.cloud import storage


def get_storage(game_scope, project_id):
    """Function to define where game artifacts are stored.
    game_scope could be "GLOBAL" or "LOCAL".
    If game_scope is "GLOBAL", artifacts are stored on the Google server.
    If game_scope is "LOCAL", artifacts are stored locally.
    """
    if game_scope == "GLOBAL":
        storage_client = storage.Client(project=project_id)

    if game_scope == "LOCAL":
        storage_client = None
    return storage_client 
