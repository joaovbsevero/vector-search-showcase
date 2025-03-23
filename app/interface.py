import secrets
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import Literal

import streamlit as st
from bson import ObjectId
from fastembed import TextEmbedding
from pinecone import Pinecone
from pymilvus import MilvusClient
from pymongo import MongoClient
from qdrant_client import QdrantClient
from settings import Settings

settings = Settings.get_settings()

pinecone_settings = settings.pinecone_database_config
milvus_settings = settings.milvus_database_config
mongo_settings = settings.mongodb_database_config
qdrant_settings = settings.qdrant_database_config


# model = SentenceTransformer(settings.embedding_model)
DATABASE_NAMES = Literal["Milvus", "Pinecone", "MongoDB", "QDrant"]
CONNECTION_TYPES = MilvusClient | MongoClient | Pinecone | QdrantClient


# Connect to DB based on user selection
def get_connection(database_name: DATABASE_NAMES) -> CONNECTION_TYPES:
    if "connections" not in st.session_state:
        st.session_state.connections = {}

    connections = st.session_state.connections
    if database_name in connections:
        return connections[database_name]

    if database_name == "Milvus":
        client = MilvusClient("milvus.db")
        client.create_collection(
            collection_name=milvus_settings.collection_name,
            dimension=384,
        )
        connections[database_name] = client
        return client

    elif database_name == "Pinecone":
        client = Pinecone(api_key=pinecone_settings.api_key)
        if not client.has_index(pinecone_settings.index_name):
            client.create_index_for_model(
                name=pinecone_settings.index_name,
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {"text": "text"},
                },  # type: ignore
            )

        connections[database_name] = client
        return client

    elif database_name == "MongoDB":
        client = MongoClient(mongo_settings.uri)
        connections[database_name] = client
        return client

    elif database_name == "QDrant":
        client = QdrantClient(":memory:")
        connections[database_name] = client
        return client


# Embedding and indexing
def index_documents(
    connection: CONNECTION_TYPES,
    documents: list[tuple[str, str]],
):
    if isinstance(connection, MilvusClient):
        embedding_model = TextEmbedding()

        vectors = list(embedding_model.embed([doc[1] for doc in documents]))
        data = [
            {
                "id": i,
                "vector": vectors[i],
                "text": documents[i][1],
                "title": documents[i][0],
            }
            for i in range(len(vectors))
        ]
        connection.insert(
            collection_name=milvus_settings.collection_name,
            data=data,
        )
    elif isinstance(connection, Pinecone):
        index = connection.Index(pinecone_settings.index_name)
        index.upsert_records(
            "namespace",
            [
                {"_id": str(ObjectId()), "title": doc[0], "text": doc[1]}
                for doc in documents
            ],
        )
    elif isinstance(connection, MongoClient):
        embedding_model = TextEmbedding()
        embeddings = list(embedding_model.embed([doc[1] for doc in documents]))
        collection = connection[mongo_settings.db_name][mongo_settings.collection_name]
        collection.insert_many(
            [
                {"text": doc[1], "title": doc[0], "embedding": emb.tolist()}
                for emb, doc in zip(embeddings, documents)
            ]
        )
    elif isinstance(connection, QdrantClient):
        connection.add(
            collection_name=qdrant_settings.collection_name,
            documents=[doc[1] for doc in documents],
            metadata=[{"title": doc[0]} for doc in documents],
            ids=[str(uuid.uuid4()) for _ in documents],
        )


# Searching
def search_documents(
    connection: CONNECTION_TYPES,
    query: str,
    top_k: int = 3,
) -> list[tuple[str, str, float]]:
    if isinstance(connection, MilvusClient):
        embedding_model = TextEmbedding()
        query_vectors = list(embedding_model.embed([query]))

        res = connection.search(
            collection_name=milvus_settings.collection_name,
            data=query_vectors,
            limit=top_k,
            output_fields=["title", "text"],
        )
        return [
            (hit["entity"]["title"], hit["entity"]["text"], hit["distance"])
            for hits in res
            for hit in hits
        ]
    elif isinstance(connection, Pinecone):
        index = connection.Index(pinecone_settings.index_name)
        results = index.search(
            namespace="namespace",
            query={
                "inputs": {
                    "text": query,
                },
                "top_k": top_k,
            },  # type: ignore
        )
        return [
            (hit["fields"]["title"], hit["fields"]["text"], hit["_score"])
            for hit in results["result"]["hits"]
        ]
    elif isinstance(connection, MongoClient):
        embedding_model = TextEmbedding()
        query_vectors = list(embedding_model.embed([query]))

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "default",
                    "path": "embedding",
                    "queryVector": query_vectors[0].tolist(),
                    "numCandidates": 100,
                    "limit": top_k,
                }
            },
            {
                "$project": {
                    "title": 1,
                    "text": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
        collection = connection[mongo_settings.db_name][mongo_settings.collection_name]
        return [
            (doc["title"], doc["text"], doc["score"])
            for doc in collection.aggregate(pipeline)
        ]
    elif isinstance(connection, QdrantClient):
        res = connection.query(
            collection_name=qdrant_settings.collection_name,
            query_text=query,
            limit=top_k,
        )
        return [(hit.metadata["title"], hit.document, hit.score) for hit in res]


# Streamlit Interface
st.title("Unified Vector DB Interface")

# File Upload - moved to top
uploaded_file = st.file_uploader(
    "Upload a ZIP file containing text documents", type=["zip"]
)

# Store documents in session state
if "docs" not in st.session_state:
    st.session_state.docs = []

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / f"{secrets.token_urlsafe(16)}.zip"
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
            docs: list[tuple[str, str]] = []
            for path in Path(tmpdir).glob("**/*.*"):
                if path.is_dir():
                    continue

                try:
                    with open(path) as doc_file:
                        docs.append((path.name, doc_file.read()))
                except Exception:
                    pass
            st.session_state.docs = docs

    st.success(f"Uploaded {len(st.session_state.docs)} documents.")

# Database selection - moved below upload
db_choice: DATABASE_NAMES = st.selectbox(
    "Select Vector Database:", ["Milvus", "Pinecone", "MongoDB", "QDrant"]
)

connection = get_connection(db_choice)

# Indexing button
if st.session_state.docs:
    if st.button("Index Documents"):
        index_documents(connection, st.session_state.docs)
        st.success(f"Indexed {len(st.session_state.docs)} documents successfully!")

# Search input
search_query = st.text_input("Search the indexed documents:")
if st.button("Search"):
    if search_query:
        results = search_documents(connection, search_query)
        for title, text, score in results:
            st.write(f"**Score:** {score:.3f} — **Title:** {title}")
            st.write(f"**Content:** \n```txt\n{text[:200]}...\n```")
    else:
        st.warning("Please enter a search query first!")
