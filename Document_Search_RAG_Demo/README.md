# Document Search with Source Citations (RAG retrieval demo)

A small semantic-search tool over public health documents. You ask a question in plain English; it returns the most relevant passages with the **file name and page number**, and says "I could not find this in the provided documents" when the question is outside the documents.

**Scope note:** This version does retrieval only. It does not use a language model to write answers, so nothing is generated or paraphrased. Adding an LLM generation step is a planned next step and has not been built yet.

## How it works
1. **Load** PDFs with `pypdf`
2. **Clean** repeated page footers with a regex
3. **Chunk** each page into 1,000-character pieces with 200 overlap; drop chunks under 200 characters (664 chunks)
4. **Embed and store** in Chroma using its default model (all-MiniLM-L6-v2)
5. **Search**: return the top 5 chunks with source and page
6. **Refuse** when the best match distance is above 1.0

## Documents used (public; download them yourself)
- NICE NG28 Type 2 diabetes in adults: management (updated Feb 2026)
- NICE NG136 Hypertension in adults: diagnosis and management (updated Feb 2026)
- Diabetes UK, Type 2 diabetes: know your risk
- WHO Global Report on Diabetes (2016)

Put them in `documents_health/` and run `python 01_load_and_chunk.py`, `python 02_build_index.py`, then `python 04_ask_nokey.py "your question"`.
Example: python 04_ask_nokey.py "What HbA1c target should be offered to adults with type 2 diabetes?"

## Evaluation (15 questions, checked by hand against the PDFs)
| Question type | Count | Best-match distance range |
|---|---|---|
| Answerable | 8 | 0.43 - 0.89 |
| Health-related, not in documents | 3 | 1.20 - 1.36 |
| Unrelated | 4 | 1.60 - 1.75 |

- Right passage in top 5 for answerable questions: **6 yes, 1 partly, 1 no** (of 8)
- Correct answer-or-refuse behaviour: **14 of 15**

Full results: `evaluation_results.csv`. The cutoff of 1.0 was chosen by looking at these same 15 questions, so it is not an independent test.

## Limitations
- The key recommendation for "first-line medicine" (NG28, page 32) was not in the top 5; related pages were returned instead.
- One question (foot-check frequency) was wrongly labelled as answerable; the documents do not state a frequency, yet the system answered. A distance cutoff can tell if a topic is covered, not whether the question is actually answered.
- Chunks are cut by character count, so they can start or end mid-sentence.
- Tables are handled poorly by text extraction.
- The WHO report's statistics are from 2014-2016; NICE guidance was updated in 2026, so documents can disagree.
- Small test set (15 questions); not a measure of general accuracy.
- Information tool only; **not medical advice**.

## Tools
Python, pypdf, ChromaDB (embeddings via all-MiniLM-L6-v2)

## Screenshots
![Good answer](answer_example.png.png)
![Refusal](refusal_example.png.png)
![Evaluation results](evaluation_results.png.png)
