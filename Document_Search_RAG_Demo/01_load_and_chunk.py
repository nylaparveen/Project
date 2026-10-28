import sys
import re

FOOTER_PATTERN = re.compile(
    r"©|notice-of-rights|conditions#|^Page \d+ of|^\d+$|\(NG\d+\)\s*$",
    re.IGNORECASE,
)

def clean_page_text(text: str) -> str:
    """Remove repeated footer/header lines that add noise."""
    lines = [ln for ln in text.splitlines() if not FOOTER_PATTERN.search(ln.strip())]
    return "\n".join(lines)


from pathlib import Path
from pypdf import PdfReader

FOLDER = sys.argv[1] if len(sys.argv) > 1 else "documents_health"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_pdf(path: Path):
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append((i, text))
    return pages


def chunk_text(text: str, size: int, overlap: int):
    chunks = []
    start = 0
    while start < len(text):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(piece)
        start += size - overlap
    return chunks


def build_chunks(folder: str):
    all_chunks = []
    for pdf_path in sorted(Path(folder).glob("*.pdf")):
        pages = load_pdf(pdf_path)
        total_chars = sum(len(t) for _, t in pages)
        file_chunks = 0
        for page_num, text in pages:
            for piece in chunk_text(clean_page_text(text), CHUNK_SIZE, CHUNK_OVERLAP):
                if len(piece) < 200:
                    continue
                all_chunks.append(
                    {"text": piece, "source": pdf_path.name, "page": page_num}
                )
                file_chunks += 1
        print(f"{pdf_path.name}: {len(pages)} pages, {total_chars} characters, {file_chunks} chunks")
        if total_chars < 500:
            print("   WARNING: almost no text found. This PDF may be a scan.")
    return all_chunks


if __name__ == "__main__":
    chunks = build_chunks(FOLDER)
    print(f"\nTotal chunks: {len(chunks)}")
    if chunks:
        mid = chunks[len(chunks) // 2]
        print(f"\nSample chunk (from {mid['source']}, page {mid['page']}):\n")
        print(mid["text"])