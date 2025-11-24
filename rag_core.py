from db import get_conn
from openai_utils import embed_text
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def retrieve(query: str, k=5):
    # 1. Vectorisation de la question
    q_emb = embed_text(query)
    
    conn = get_conn()
    with conn.cursor() as cur:
        # 2. Recherche vectorielle (Cosine Distance)
        # L'opérateur <=> calcule la distance. 
        # On fait (1 - distance) pour obtenir un score de similarité (1 = identique).
        cur.execute("""
            SELECT source, chunk, modality, 
                   1 - (embedding <=> %s::vector) AS score
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (q_emb, q_emb, k))
        
        return cur.fetchall()

def answer(query: str, k=5):
    # 1. Récupération du contexte
    rows = retrieve(query, k=k)
    
    # Construction du bloc de contexte (Source 242)
    context = "\n\n".join([f"[{m}] {c}" for _, c, m, _ in rows])
    
    # 2. Construction du Prompt
    prompt = f"""
    Tu es un assistant RAG multimodal.
    Utilise STRICTEMENT le contexte pour repondre.
    
    Contexte:
    {context}
    
    Question:
    {query}
    
    Reponse:
    """
    
    # 3. Appel au LLM (Syntaxe spécifique du PDF)
    resp = client.responses.create(
        model="gpt-5",
        input=prompt
    )
    
    return resp.output_text, rows