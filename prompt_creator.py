import numpy as np
import openai
import pandas as pd
from document_embeddings_obtainer import get_query_embedding, load_embeddings
from transformers import GPT2TokenizerFast

MAX_SECTION_LEN = 1500
SEPARATOR = "\n* "


def vector_similarity(x: list[float], y: list[float]) -> float:
    """
    We could use cosine similarity or dot product to calculate the similarity between vectors.
    In practice, we have found it makes little difference.
    """
    return np.dot(np.array(x), np.array(y))


def order_document_sections_by_query_similarity(
    query: str, contexts: dict[(str, str), np.array]
) -> list[(float, (str, str))]:
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections.

    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_query_embedding(query)

    document_similarities = sorted(
        [
            (vector_similarity(query_embedding, doc_embedding), doc_index)
            for doc_index, doc_embedding in contexts.items()
        ],
        reverse=True,
    )

    return document_similarities


def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame) -> str:
    """
    Fetch relevant
    """
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    separator_len = len(tokenizer.tokenize(SEPARATOR))
    most_relevant_document_sections = order_document_sections_by_query_similarity(
        question, context_embeddings
    )

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.
        document_section = df.loc[section_index]

        chosen_sections_len += document_section.tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break

        chosen_sections.append(SEPARATOR + document_section.content.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))

    # Useful diagnostic information
    print(f"Selected {len(chosen_sections)} document sections:")
    print("\n".join(chosen_sections_indexes))

    header = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""

    return header + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:"


COMPLETIONS_MODEL = "text-davinci-002"
COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 300,
    "model": COMPLETIONS_MODEL,
}


def answer_query_with_context(
    query: str,
    df: pd.DataFrame,
    document_embeddings: dict[(str, str), np.array],
    show_prompt: bool = False,
) -> str:
    prompt = construct_prompt(query, document_embeddings, df)

    if show_prompt:
        print(prompt)

    response = openai.Completion.create(prompt=prompt, **COMPLETIONS_API_PARAMS)

    return response["choices"][0]["text"].strip(" \n")


def get_answer(question: str):
    document_embeddings = load_embeddings("csv/api-sendesk-data-embeddings.csv")
    df = pd.read_csv("csv/api-sendesk-data.csv")
    df = df.set_index(["title", "heading"])

    anwser = answer_query_with_context(question, df, document_embeddings)
    return anwser