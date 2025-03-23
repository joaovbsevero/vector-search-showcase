# 🧠 Unified Vector DB Interface

A Streamlit-based web interface that allows you to upload and index text documents across multiple vector databases including **Milvus**, **Pinecone**, **MongoDB**, and **QDrant**. Supports searching over embedded content using the `fastembed` library for embeddings.

---

## 🚀 Features

- 📂 Upload a `.zip` file containing textual documents.
- 🧠 Embed and index documents using multiple vector DBs.
- 🔍 Perform semantic search over indexed documents.
- 🔄 Pluggable vector database backends.
- 🧹 Easily extendable for new DBs or embedding models.

---

## 💠 Requirements

- Docker (recommended)
- Alternatively: Python 3.11+ with `uv`, `streamlit`, and relevant DB clients

---

## 🐳 Run with Docker

### 1. Build the Docker image

```bash
docker build -t unified_vector_db .
```

### 2. Run the container

```bash
docker run -p 8501:8501 \
  -e VECTOR_SEARCH_APP_STREAMLIT_SERVER_PORT=8501 \
  -e VECTOR_SEARCH_APP_STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
  unified_vector_db
```

Or use Docker Compose:

```bash
docker compose up --build unified_vector_db
```

---

## 🧬 Environment Variables

Copy `example.env` to `.env` and fill in your credentials:

```bash
cp example.env .env
```

```env
# Qdrant configuration
VECTOR_SEARCH_APP_QDRANT_COLLECTION_NAME=documents

# Milvus configuration
VECTOR_SEARCH_APP_MILVUS_COLLECTION_NAME=documents

# MongoDB configuration
VECTOR_SEARCH_APP_MONGODB_URI=mongodb+srv://usr:pwd@cluster
VECTOR_SEARCH_APP_MONGODB_DB_NAME=vector_db
VECTOR_SEARCH_APP_MONGODB_COLLECTION_NAME=documents

# Pinecone configuration
VECTOR_SEARCH_APP_PINECONE_API_KEY=your-pinecone-key
VECTOR_SEARCH_APP_PINECONE_INDEX_NAME=documents

# Streamlit config
VECTOR_SEARCH_APP_STREAMLIT_SERVER_PORT=8501
VECTOR_SEARCH_APP_STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

These are automatically used by the app at runtime.

---

## 🧪 Usage

1. Open the Streamlit app in your browser: `http://localhost:8501`
2. Upload a `.zip` containing text files (e.g., `.txt`, `.md`)
3. Select the vector database to use
4. Click **“Index Documents”**
5. Use the search input to query the indexed documents

---

## 📁 Project Structure

```bash
.
├── Dockerfile
├── README.md
├── app
│   ├── __init__.py
│   ├── interface.py
│   └── settings.py
├── compose.yml
├── example.env
├── pyproject.toml
└── requirements.lock
```
