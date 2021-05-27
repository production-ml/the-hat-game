import json
import os
import shutil
import urllib.request
import zipfile
from glob import glob

from google.cloud import storage
from tqdm.auto import tqdm

from settings import DATA_PATH, STORAGE_CLIENT


def check_create_dir(path):
    try:
        os.stat(path)
    except FileExistsError:
        os.mkdir(path)


def upload_unzip(url):
    file_name = DATA_PATH / url.split("/")[-1:][0]
    urllib.request.urlretrieve(url, filename=file_name)
    shutil.rmtree(DATA_PATH / "texts")
    with zipfile.ZipFile(file_name, "r") as zip_ref:
        zip_ref.extractall(DATA_PATH / "texts")


def unzip(file_name, folder):
    check_create_dir(folder)
    shutil.rmtree(folder)
    with zipfile.ZipFile(file_name, "r") as zip_ref:
        zip_ref.extractall(folder)


def merge_all_files(folder, file_name):
    with open(file_name, "w") as write_stream:
        files = glob(str(folder / "**" / "*.json"))

        for path in tqdm(files[:]):
            try:
                with open(path, encoding="utf-8") as stream:
                    text = json.load(stream)["text"]
                    print(text, file=write_stream)
            except UnicodeEncodeError:
                pass


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def split_file(file_name, folder, num_parts):
    ln = file_len(file_name)

    lines_per_file = ln // num_parts

    check_create_dir(folder)

    smallfile = None
    with open(file_name) as bigfile:
        for lineno, line in enumerate(bigfile):
            if lineno % lines_per_file == 0:
                if smallfile:
                    smallfile.close()
                small_filename = folder / f"part_{lineno + lines_per_file}.txt"
                smallfile = open(small_filename, "w")
            smallfile.write(line)
        if smallfile:
            smallfile.close()


def upload_splits_to_store(folder, bucket_name):
    files = glob(str(folder / "*.txt"))
    for f in tqdm(files):
        upload_blob(bucket_name, str(f), os.path.basename(f))


def upload_blob(bucket_name, source_file_name, destination_blob_name, storage_client=STORAGE_CLIENT):
    """Uploads a file to the bucket. https://cloud.google.com/storage/docs/"""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def download_form_blob(
    bucket_name,
    destination_directory,
    file_name,
    prefix=None,
    storage_client=STORAGE_CLIENT,
):
    """Takes the data from your GCS Bucket and puts it into the working directory of your notebook"""
    os.makedirs(destination_directory, exist_ok=True)
    full_file_path = os.path.join(destination_directory, file_name)
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    for blob in blobs:
        blob.download_to_filename(full_file_path)


def copy_blob(
    bucket_name,
    blob_name,
    destination_bucket_name,
    destination_blob_name,
    storage_client=STORAGE_CLIENT,
):
    """Copies a blob from one bucket to another with a new name."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    # destination_bucket_name = "destination-bucket-name"
    # destination_blob_name = "destination-object-name"

    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(blob_name)
    destination_bucket = storage_client.bucket(destination_bucket_name)

    source_bucket.copy_blob(source_blob, destination_bucket, destination_blob_name)


def list_blobs(bucket_name, storage_client=STORAGE_CLIENT):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    return [b.name for b in blobs]


def add_new_text(bucket_name, destination_bucket_name):
    all_files = list_blobs(bucket_name)
    copied_files = list_blobs(destination_bucket_name)
    to_copy = sorted(set(all_files) - set(copied_files))[0]
    copy_blob(bucket_name, to_copy, destination_bucket_name, to_copy)


def check_or_create_bucket(bucket, storage_client=STORAGE_CLIENT):
    bucket = storage.Bucket(storage_client, name=bucket)
    if not bucket.exists():
        bucket.create(location="EU")
