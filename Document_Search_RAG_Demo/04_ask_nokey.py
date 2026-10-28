import sys
import chromadb

FOLDER = "documents_health"
TOP_K = 5
MAX_DISTANCE = 1.0   # above this, we treat the question as "not in the documents"

question = " ".join(sys.argv[1:]) or "What is the first-line medicine for type 2 diabetes?"

collection = chromadb.PersistentClient(path="chroma_db").get_collection(FOLDER)
results = collection.query(query_texts=[question], n_results=TOP_K)

docs = results["documents"][0]
metas = results["metadatas"][0]
dists = results["distances"][0]

print(f"Question: {question}\n")
print("Distances of the top results:", [round(d, 3) for d in dists], "\n")

if dists[0] > MAX_DISTANCE:
    print("I could not find this in the provided documents.")
else:
    print("Most relevant passages (check each source before relying on it):\n")
    for text, meta, dist in zip(docs, metas, dists):
        print(f"[{meta['source']}, page {meta['page']}]  distance {dist:.3f}")
        print(text)
        print("-" * 60)