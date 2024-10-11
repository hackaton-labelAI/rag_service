def generate_doc_context_prompt(doc_content):
    prompt = f"""
<document>
{doc_content}
</document>
"""
    return prompt


def generate_chunks_context_prompt(chunk):
    prompt = f"""
Here is the chunk we want to situate within the whole document
<chunk>
{chunk}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else. You MUST use less than 200 tokens
    """
    return prompt