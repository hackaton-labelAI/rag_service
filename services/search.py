from services.vector_bd import VectorDB

vector_db = VectorDB()
vector_db.load_db()

async def search(id, question):
    vector_search = vector_db.search(question)
    elastic_search =
    pass