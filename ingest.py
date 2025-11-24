import os
import glob
from tqdm import tqdm
from pypdf import PdfReader
from db import get_conn
from openai_utils import embed_text, caption_image

# Configuration du découpage de texte
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

def chunk_text(text: str):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + CHUNK_SIZE])
        i += (CHUNK_SIZE - CHUNK_OVERLAP)
    return chunks

def ingest_pdf(path: str):
    reader = PdfReader(path)

    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return chunk_text(full_text)

def ingest_images(paths: list[str]):
    image_chunks = []
    for p in paths:
        cap = caption_image(p)
        image_chunks.append((p, cap))
    return image_chunks

def save_chunk(conn, source, chunk, modality, emb):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO documents (source, chunk, modality, embedding)
            VALUES (%s, %s, %s, %s)
        """, (source, chunk, modality, emb))
    conn.commit()

def main(data_dir="data"):
    conn = get_conn()
    
    # Récupération des fichiers dans le dossier 'data'
    pdfs = glob.glob(os.path.join(data_dir, "*.pdf"))
    imgs = glob.glob(os.path.join(data_dir, "*.png")) + glob.glob(os.path.join(data_dir, "*.jpg"))

    # 1. Ingestion des PDFs (Texte)
    for pdf in tqdm(pdfs, desc="PDF ingestion"):
        for c in ingest_pdf(pdf):
            emb = embed_text(c)
            save_chunk(conn, pdf, c, "text", emb)

    # ingest_images renvoie une liste de tuples (chemin_image, caption)
    for img_path, cap in tqdm(ingest_images(imgs), desc="Image ingestion"):
        emb = embed_text(cap)
        save_chunk(conn, img_path, cap, "image", emb)

    print("Ingestion terminée.")

if __name__ == "__main__":
    # Assurez-vous d'avoir un dossier 'data' avec vos fichiers dedans
    main()