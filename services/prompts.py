def generate_chunks_prompt(text):
    prompt = f"""
{text}
_____________
The size of one fact should not exceed one paragraph, one or two sentences will be enough.
You need to find out the main topic of the discussion by specifying the object of the discussion.
You need to take text as input and extract key facts from it and add for each facts main topic and return a response.
Your response should be a markdown list, eg: - foo\n- bar\n- baz'
Do not translate the facts, use the language in which this document is written.
Above is the text you need to process.
"""
    return prompt


def generate_chunks_context_prompt(chunk):
    prompt = f"""
Here is the chunk we want to situate within the whole document
<chunk>
{chunk}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else.
    """
    return prompt

prompt_multiplication= """
    Необходимо придумать 4 других интерпритации вопроса и записать их в массив
    Вопрос:
    %s
    
    В ответе должен быть только 5 вопросов: изначальный вопрос и других 4 перефразированных вопросов:
    формат ответа: число, точка, пробел, перефразированый текст, перевод строки.
    id. <перефразированый вопрос>
    
    """


def generate_question_prompt(question):
    return f"""
    Ответь на следующий вопрос: <вопрос>{question}</вопрос>. Запрещено использовать ненормативную лексику. 
"""