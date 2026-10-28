import sys
import chromadb

FOLDER = "documents_health"
TOP_K = 3

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(FOLDER)

question = " ".join(sys.argv[1:]) or "What is the first-line medicine for type 2 diabetes?"
print(f"Question: {question}\n")

results = collection.query(query_texts=[question], n_results=TOP_K)

for rank in range(TOP_K):
    text = results["documents"][0][rank]
    meta = results["metadatas"][0][rank]
    dist = results["distances"][0][rank]
    print(f"--- Result {rank + 1} | {meta['source']} | page {meta['page']} | distance {dist:.3f} ---")
    print(text)
    print()