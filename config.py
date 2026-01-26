from pathlib import Path

# projects directories
ADDON_DIR = Path(__file__).parent.resolve()

DATASET_DIR = ADDON_DIR / "dataset" 
DATASET_DIR.mkdir(exist_ok=True)

VECTORSTORE_DIR = ADDON_DIR / "Blender500_vectorstore"
VECTORSTORE_DIR.mkdir(exist_ok=True)

EMBEDDINGS_BACKUP_DIR = VECTORSTORE_DIR / "embeddings"
EMBEDDINGS_BACKUP_DIR.mkdir(exist_ok=True)

# vector db collection
VECTOR_NAME = "Blender500_embeddings"
COLLECTION_NAME = "Blender500_collection"
EMBEDDING_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_DIMENSION = 768

# dataset
DATASET_JSON = DATASET_DIR / "dataset.json"