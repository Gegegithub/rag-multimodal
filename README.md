# RAG Multimodal

Systeme de Retrieval-Augmented Generation (RAG) avec support multimodal permettant d'indexer et d'interroger des documents PDF et des images.

## Description

Ce projet implémente un pipeline RAG complet qui :

- Extrait le texte des fichiers PDF
- Génère des descriptions automatiques des images via GPT-4o
- Stocke les embeddings dans une base de données vectorielle (PostgreSQL + pgvector)
- Permet de poser des questions en langage naturel via une interface web

## Architecture

```
Documents (PDFs, Images)
        |
        v
+------------------+
|    Ingestion     |  <- ingest.py
|  - Extraction    |
|  - Chunking      |
|  - Captioning    |
+------------------+
        |
        v
+------------------+
|    Embeddings    |  <- openai_utils.py
| text-embedding-  |
|    3-small       |
+------------------+
        |
        v
+------------------+
|   PostgreSQL     |  <- db.py
|   + pgvector     |
+------------------+
        |
        v
+------------------+
|   Retrieval &    |  <- rag_core.py
|   Generation     |
+------------------+
        |
        v
+------------------+
|   Interface      |  <- app.py
|   Streamlit      |
+------------------+
```

## Prérequis

- Python 3.10+
- Docker et Docker Compose
- Clé API OpenAI

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/rag-multimodal.git
cd rag-multimodal
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
OPENAI_API_KEY=votre-cle-api-openai
PG_HOST=localhost
PG_PORT=5433
PG_DB=ragdb
PG_USER=raguser
PG_PASSWORD=ragpass
```

### 5. Lancer la base de données

```bash
docker-compose up -d
```

## Utilisation

### Ingestion des documents

Placer vos fichiers PDF et images (PNG, JPG) dans le dossier `data/`, puis exécuter :

```bash
python ingest.py
```

Le script va :
- Extraire le texte des PDFs et le découper en chunks de 800 caractères
- Générer des descriptions pour chaque image via GPT-4o
- Créer les embeddings et les stocker dans la base de données

### Lancer l'interface web

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## Structure du projet

```
rag-multimodal/
├── app.py              # Interface Streamlit
├── rag_core.py         # Logique RAG (retrieval + generation)
├── ingest.py           # Pipeline d'ingestion des documents
├── db.py               # Connexion PostgreSQL
├── openai_utils.py     # Utilitaires OpenAI (embeddings, captioning)
├── docker-compose.yml  # Configuration PostgreSQL + pgvector
├── requirements.txt    # Dépendances Python
├── data/               # Dossier des documents à indexer
└── .env                # Variables d'environnement (non versionné)
```

## Description des fichiers

### app.py

Point d'entree de l'application. Ce fichier cree l'interface web avec Streamlit :
- Affiche un champ de saisie pour poser des questions
- Appelle le module `rag_core` pour obtenir les reponses
- Affiche la reponse generee par le LLM
- Montre les chunks recuperes avec leur score de similarite et leur modalite (texte ou image)

### rag_core.py

Coeur du systeme RAG contenant deux fonctions principales :
- `retrieve(query, k)` : Convertit la question en embedding, effectue une recherche par similarite cosinus dans PostgreSQL et retourne les k chunks les plus pertinents
- `answer(query, k)` : Orchestre le pipeline complet en appelant `retrieve()`, construisant le contexte a partir des chunks, puis envoyant le tout au LLM pour generer une reponse

### ingest.py

Pipeline d'ingestion des documents avec les fonctions :
- `chunk_text(text, size, overlap)` : Decoupe le texte en morceaux de taille fixe avec chevauchement pour preserver le contexte
- `ingest_pdf(path)` : Extrait le texte de chaque page d'un PDF via pypdf, le decoupe en chunks et les stocke
- `ingest_images(path)` : Envoie l'image a GPT-4o pour obtenir une description textuelle, puis stocke cette description
- `save_chunk(source, chunk, modality)` : Genere l'embedding du chunk et l'insere dans la base de donnees
- `main()` : Parcourt le dossier `data/` et traite tous les fichiers PDF et images

### db.py

Module de connexion a la base de donnees :
- `get_conn()` : Cree une connexion PostgreSQL en utilisant les variables d'environnement et enregistre l'extension pgvector pour manipuler les vecteurs

### openai_utils.py

Utilitaires pour interagir avec l'API OpenAI :
- `embed_text(text)` : Convertit un texte en vecteur de 1536 dimensions via le modele text-embedding-3-small
- `image_to_base64(path)` : Encode une image en base64 pour l'envoi a l'API
- `caption_image(path)` : Envoie l'image a GPT-4o et retourne une description textuelle de 2-3 phrases optimisee pour la recherche

### docker-compose.yml

Configuration Docker pour lancer PostgreSQL avec l'extension pgvector :
- Utilise l'image `pgvector/pgvector:pg16`
- Expose le port 5433 pour eviter les conflits avec une installation PostgreSQL locale
- Configure un volume persistant pour les donnees

### requirements.txt

Liste des dependances Python necessaires :
- `openai` : Client API OpenAI
- `psycopg2-binary` : Driver PostgreSQL
- `pgvector` : Support des vecteurs dans Python
- `pypdf` : Extraction de texte des PDFs
- `pillow` : Manipulation d'images
- `python-dotenv` : Chargement des variables d'environnement
- `tqdm` : Barres de progression
- `streamlit` : Framework d'interface web

## Technologies

| Composant | Technologie |
|-----------|-------------|
| Interface | Streamlit |
| Base vectorielle | PostgreSQL 16 + pgvector |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | OpenAI GPT-4o / GPT-4 |
| Extraction PDF | pypdf |
| Traitement images | Pillow |

## Fonctionnement

### Ingestion

1. Les PDFs sont parsés et le texte est extrait page par page
2. Le texte est découpé en chunks de 800 caractères avec un chevauchement de 100 caractères
3. Les images sont envoyées à GPT-4o pour générer une description textuelle
4. Chaque chunk (texte ou description d'image) est converti en vecteur via l'API OpenAI
5. Les vecteurs sont stockés dans PostgreSQL avec leur source et modalité

### Requête

1. La question de l'utilisateur est convertie en vecteur
2. Une recherche par similarité cosinus récupère les 5 chunks les plus pertinents
3. Les chunks sont assemblés en contexte
4. Le contexte et la question sont envoyés au LLM
5. La réponse est affichée avec les sources utilisées

