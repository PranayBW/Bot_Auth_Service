from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """
    Lazily load the embedding model.

    Importing the FastAPI app should not trigger network/model downloads.
    """

    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model
