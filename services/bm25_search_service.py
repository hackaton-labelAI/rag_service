import os

from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

from services.vector_bd import VectorDB


# indexing document
# search
# add new index


def get_index(index_dir='indexdir'):
    """
     если индекс  сущетвует, то подгружаем его из файлов
     если нет, то создаем с нуля
    """
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    if not os.listdir(index_dir) or os.listdir(index_dir) == ['.DS_Store']:
        schema = Schema(
            doc_id=TEXT(stored=True),
            chunk_id=TEXT(stored=True),
            original_index=TEXT(stored=True),
            original_content=TEXT(stored=True),
            contextualized_content=TEXT(stored=True),
            version=TEXT(stored=True)
        )
        ix = create_in(index_dir, schema)
    else:
        ix = open_dir(index_dir)
    return ix


def indexing_document(index, documents):
    writer = index.writer()
    for doc in documents:
        writer.add_document(doc_id=u"{}".format(doc['doc_id']),
                            chunk_id=u"{}".format(doc['chunk_id']),
                            original_index=u"{}".format(doc['original_index']),
                            original_content=u"{}".format(doc['original_content']),
                            contextualized_content=u"{}".format(doc['contextualized_content']),
                            version=u"{}".format(doc['version'])
                            )

    writer.commit()


def search(index, query_string):
    '''
    на выходе это
    {
                'doc_id': doc['doc_id'],
                # 'original_uuid': doc['original_uuid'],
                'chunk_id': chunk['chunk_id'],
                'original_index': chunk['original_index'],
                'original_content': chunk['content'],
                'contextualized_content': f"{chunk['content']}\n\n{contextualized_text}",
                'version': chunk['version']
                # 'version': 1
            }
    '''

    with index.searcher() as searcher:
        query = QueryParser("original_content", index.schema).parse(query_string)
        results = searcher.search(query)
        if len(results) >= 10:
            top_results = [result.fields() for result in results[:10]]
        else:
            top_results = [result.fields() for result in results[:len(results)]]
        return top_results


if __name__=='__main__':
    ix = get_index('../data/bm')
    vec = VectorDB()
    vec.load_db()
    indexing_document(ix, vec.chunks)
    print(search(ix, 'РЖД'))
    print(len(search(ix, 'РЖД')))


