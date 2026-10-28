
import csv
import sys

import chromadb

FOLDER = sys.argv[1] if len(sys.argv) > 1 else "documents_health"
TOP_K = 5
MAX_DISTANCE = 1.0   # same cutoff as 04_ask_nokey.py
OUT_FILE = "evaluation_results.csv"

# (question, expected type)
# "answerable"  = I expect the answer to be in the documents (YOU must confirm in the PDF)
# "near-miss"   = health topic, but not covered by these documents
# "unrelated"   = nothing to do with health
QUESTIONS = [
    ("What is the first-line medicine for adults with type 2 diabetes?", "answerable"),
    ("What blood pressure level is used to diagnose hypertension?", "answerable"),
    ("What HbA1c target should be offered to adults with type 2 diabetes?", "answerable"),
    ("How often should people with diabetes have their feet checked?", "answerable"),
    ("What are the symptoms of type 2 diabetes?", "answerable"),
    ("When should ambulatory blood pressure monitoring be offered?", "answerable"),
    ("How many people worldwide were estimated to have diabetes in the WHO report?", "answerable"),
    ("What lifestyle advice is given to people with high blood pressure?", "answerable"),
    ("What is the recommended treatment for asthma?", "near-miss"),
    ("At what age should cancer screening start?", "near-miss"),
    ("What is the childhood vaccination schedule?", "near-miss"),
    ("Who won the football World Cup in 2018?", "unrelated"),
    ("What is the capital of Australia?", "unrelated"),
    ("How do I bake a chocolate cake?", "unrelated"),
    ("What is the best programming language for beginners?", "unrelated"),
]

collection = chromadb.PersistentClient(path="chroma_db").get_collection(FOLDER)

rows = []
distances_by_type = {"answerable": [], "near-miss": [], "unrelated": []}

for question, q_type in QUESTIONS:
    results = collection.query(query_texts=[question], n_results=TOP_K)
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    best = dists[0]
    distances_by_type[q_type].append(best)

    sources = [f"{m['source']} p{m['page']}" for m in metas]
    rows.append({
        "question": question,
        "expected_type": q_type,
        "best_distance": round(best, 3),
        "top_3_sources": " | ".join(sources[:3]),
        "top_4_5_sources": " | ".join(sources[3:]),
        "system_response": "refused" if best > MAX_DISTANCE else "answered",
        "right_passage_in_top_5 (yes/no)": "",   # fill in by hand
        "refusal_correct (yes/no)": "",          # fill in by hand
    })

# utf-8-sig so Excel opens it correctly
with open(OUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
print(f"Saved {len(rows)} rows to {OUT_FILE}\n")

# Show the distance range for each question type
print(f"Best-distance range per question type (cutoff = {MAX_DISTANCE}):")
for q_type, ds in distances_by_type.items():
    print(f"  {q_type:11s} n={len(ds)}  min={min(ds):.3f}  max={max(ds):.3f}")

# Is there a gap between answerable and the rest?
ans_max = max(distances_by_type["answerable"])
other_min = min(distances_by_type["near-miss"] + distances_by_type["unrelated"])
near_min = min(distances_by_type["near-miss"])
print()
if ans_max < other_min:
    mid = (ans_max + other_min) / 2
    print(f"Answerable questions all sit below the others (max {ans_max:.3f} < {other_min:.3f}).")
    print(f"A cutoff around {mid:.2f} would separate them on THIS small set.")
else:
    print(f"The ranges overlap: an answerable question reaches {ans_max:.3f}, "
          f"but another type starts at {other_min:.3f}.")
    print("No single cutoff separates them cleanly on this set.")
if near_min <= MAX_DISTANCE:
    print(f"Warning: the closest near-miss question ({near_min:.3f}) is under {MAX_DISTANCE}, "
          "so the system would answer it instead of refusing.")
print("\nThese numbers come from only 15 questions and my labels are unchecked.")
print("Now open evaluation_results.csv and fill in the last two columns by checking the PDFs.")
