def get_prompt(topic: str, subtopic: str, resp_length: str, query: str, language: str):
    return f"""
    You are an expert in {topic}
    Answer the question: {query}
    Answer in {language}
    You may answer in {resp_length}
    answer:
    """