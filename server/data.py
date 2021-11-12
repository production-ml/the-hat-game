import json
import os
import re
import shutil
import urllib.request
import zipfile
from collections import Counter
from glob import glob
from typing import List

from google.cloud import storage
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from tqdm.auto import tqdm

from settings_server import BUCKET_DAILY, BUCKET_SPLIT_TEXTS, DATA_PATH
from settings_server import GLOBAL_VOCAB_PATH as VOCAB_PATH
from settings_server import STORAGE_CLIENT

STOP_WORDS = stopwords.words("english")
LEMMATIZER = WordNetLemmatizer()


def sent_2_words(sent: str) -> List[str]:
    sent = sent.lower()
    sent = re.sub("[^a-z]+", " ", sent)
    words = word_tokenize(sent)
    words = [LEMMATIZER.lemmatize(word) for word in words if ((word not in STOP_WORDS) and len(word.strip()) > 3)]
    return words


def corpus_to_words(file_path: str):
    my_counter: Counter = Counter()
    with open(file_path, "r", encoding="utf-8") as fl:
        for sent in tqdm(fl, desc="Precess file"):
            my_counter.update(sent_2_words(sent))

    max_cnt = max(count for word, count in my_counter.items()) / 10
    min_count = max([10, max_cnt / 100])

    selected_words = [word for word, count in my_counter.items() if (min_count < count <= max_cnt)]
    return selected_words


def save_words(selected_words, vocab_path: str = str(VOCAB_PATH)):
    with open(vocab_path, "w", encoding="utf-8") as fl:
        for w in selected_words:
            fl.write(w + "\n")


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


def download_blob(bucket_name, source_blob_name, destination_file_name, storage_client=STORAGE_CLIENT):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


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


def add_new_text(bucket_name=BUCKET_SPLIT_TEXTS, destination_bucket_name=BUCKET_DAILY):
    print("Update_vocab")
    all_files = list_blobs(bucket_name)
    copied_files = list_blobs(destination_bucket_name)
    to_copy = sorted(set(all_files) - set(copied_files))[0]
    print(to_copy)
    download_blob(bucket_name, to_copy, DATA_PATH / to_copy)
    words = corpus_to_words(DATA_PATH / to_copy)
    save_words(words)
    copy_blob(bucket_name, to_copy, destination_bucket_name, to_copy)


def check_or_create_bucket(bucket, storage_client=STORAGE_CLIENT):
    bucket = storage.Bucket(storage_client, name=bucket)
    if not bucket.exists():
        bucket.create(location="EU")
