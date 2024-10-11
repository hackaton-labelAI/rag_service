import os

from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir


def get_index():
    if not os.listdir("indexdir") or os.listdir("indexdir") == ['.DS_Store']:
        schema = Schema(chunk_text=TEXT(stored=True), context=TEXT(stored=True), id=TEXT(stored=True))
        ix = create_in("indexdir", schema)
    else:
        ix = open_dir("indexdir")
    return ix