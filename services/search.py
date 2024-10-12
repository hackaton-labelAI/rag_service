from services.bm25_search_service import get_index, indexing_document
from services.find_service import ranking
from services.vector_bd import VectorDB
from services.bm25_search_service import search as bm25_search
vector_db = VectorDB()
vector_db.load_db()

ix = get_index('../data/bm')
vec = VectorDB()
vec.load_db()
indexing_document(ix, vec.chunks)


async def search(id, question):
    vector_search =await vector_db.search(question)
    elastic_search = bm25_search(ix, question)
    unique_objects = {}

    for item in vector_search:
        unique_objects[item['chunk_id']] = item


    for item in elastic_search:
        unique_objects[item['chunk_id']] = item

    return list(unique_objects.values())
