prompt_multiplication= """
    Необходимо придумать 4 других интерпритации вопроса и записать их в массив
    Вопрос:
    %s

    В ответе должен быть массив из 5 вопросов: изначальный вопрос и других 4 перефразированных вопросов:
    json
    {
      'arr': <пересчитаное количество>
    }
    """