from typing import Iterable
from langchain.docstore.document import Document

def split_text(text: str, chunk_size, chunk_overlap):
    sentence_list = text.split('.')
    output = []
    curr_sentence = ""
    for i in range(len(sentence_list)):
        if len(curr_sentence)>=chunk_size or i==len(sentence_list)-1:
            output.append(curr_sentence)
            curr_sentence = ""

            for j in range(i-chunk_overlap, min(i, len(sentence_list))):
                curr_sentence+=sentence_list[j]

        curr_sentence += sentence_list[i]+"."
    
    return output

def sentence_splitter(document: Iterable[Document], chunk_size: int = 300, chunk_overlap:int = 1) -> list[Document]:
    """
    Split text based on sentences.
    """
    output = []
    for doc in document:
        for sentence in split_text(doc.page_content, chunk_size=chunk_size, chunk_overlap=chunk_overlap):
            output.append(Document(
                page_content=sentence,
                metadata=doc.metadata
            ))
    return output


