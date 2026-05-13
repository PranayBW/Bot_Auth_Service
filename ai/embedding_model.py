from sentence_transformers import (
    SentenceTransformer
)

# ----------------------------------------------------
# LOAD LIGHTWEIGHT MODEL
# ----------------------------------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)