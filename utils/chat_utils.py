def get_prompt(topic: str, subtopic: str, resp_length: str, query: str, language: str):
    return f"""
    You are an expert in {topic} who specialises in {subtopic}
    Answer the question: {query}
    Answer in {language}
    Answer in {resp_length}
    """