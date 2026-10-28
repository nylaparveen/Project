import sys
import importlib
import chromadb

chunker = importlib.import_module("01_load_and_chunk")

FOLDER = sys.argv[1] if len(sys.argv) > 1 else "documents_health"
DB_PATH = "chroma_db"

chunks = chunker.build_chunks(FOLDER)

client = chromadb.PersistentClient(path=DB_PATH)
# start fresh each time so we don't get duplicates
try:
    client.delete_collection(FOLDER)
except Exception:
    pass
collection = client.create_collection(FOLDER)

BATCH = 200
for i in range(0, len(chunks), BATCH):
    batch = chunks[i:i + BATCH]
    collection.add(
        ids=[f"{c['source']}_p{c['page']}_{i + j}" for j, c in enumerate(batch)],
        documents=[c["text"] for c in batch],
        metadatas=[{"source": c["source"], "page": c["page"]} for c in batch],
    )
    print(f"Stored {min(i + BATCH, len(chunks))} / {len(chunks)} chunks")

print(f"\nDone. Collection '{FOLDER}' now holds {collection.count()} chunks.")