# RAG Decisions v0

**Status:** Proposed. Final choice of the embedding model is made with the gold-set results below, before the first document is ingested.

## 1. Embedding model

The schema stores embeddings as `vector(384)` in `knowledge_chunks`, so any model with 384-dimensional output fits without a schema change.

| | Proposed default | Candidate to compare |
|---|---|---|
| Model | `sentence-transformers/all-MiniLM-L6-v2` | `BAAI/bge-small-en-v1.5` |
| Output dimension | 384 | 384 |
| Where it runs | Locally on CPU | Locally on CPU |

Check the current model cards for license, maximum input length and query-prefix requirements before use (the BGE models recommend a query instruction for retrieval).

**Why local models:** the planned cloud VM has no GPU, small models run acceptably on CPU, there is no per-call cost, and the knowledge base is small. The hosted LLM stays behind its provider-independent interface; embeddings get the same treatment through an `EmbeddingProvider` interface so the model can be changed.

## 2. How the choice is made

1. Build the gold set of 30 to 50 questions (scope 6.5) with the expected source for each.
2. Ingest the knowledge sources once per candidate model into a scratch database.
3. For each model report Recall@5 and MRR over the in-scope and machine-aware questions.
4. Choose the model with the better numbers. Prefer the default if the difference is small.
5. Record the choice here and set `knowledge_chunks.embedding_model` on every ingested chunk.

## 3. If a model with another dimension is needed

Change `vector(384)` and rebuild the HNSW index in the schema **before the first ingestion**, while the table is empty. After ingestion a dimension change means re-embedding every chunk.

## 4. Open items

- Chunk size and overlap, decided together with the gold set.
- Whether to add keyword search next to vector search if retrieval metrics are weak for exact terms such as sensor names.