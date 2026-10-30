def validate_request(question, max_length=1000):
    if not isinstance(question, str):
        raise TypeError("Question must be text.")
    question = question.strip()
    if not question:
        raise ValueError("Question cannot be empty.")
    if len(question) > max_length:
        raise ValueError("Question exceeds permitted length.")
    return question
