from services.bm25_search_service import ElasticsearchBM25
from services.find_service import ranking
from services.vector_bd import VectorDB

vector_db = VectorDB()
vector_db.load_db()

bm25 = ElasticsearchBM25()

async def search(id, question):
    vector_search = vector_db.search(question)
    elastic_search = bm25.search(question)
    unique_objects = {}

    for item in vector_search:
        unique_objects[item['chunk_id']] = item


    for item in elastic_search:
        unique_objects[item['chunk_id']] = item

    await ranking(question, list(unique_objects.values()))


async def ranking(question, chunks):

