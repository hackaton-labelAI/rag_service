def generate_doc_context_promt(doc_content):
    promt = f"""
<document>
{doc_content}
</document>
"""
    return promt


def generate_chunks_context_promt(chunk):
    promt = f"""
Here is the chunk we want to situate within the whole document
<chunk>
{chunk}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else.
    """
    return promt