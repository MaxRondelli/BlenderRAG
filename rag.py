import json
from pathlib import Path
from typing import Optional, List, Tuple

# dependency checking
try:
    from sentence_transformers import SentenceTransformer
    from .vector_store import VectorStore
    from datapizza.core.vectorstore import Distance
    DEPENDENCIES_OK = True
    DEPENDENCY_ERROR = None
except ImportError as e:
    DEPENDENCIES_OK = False
    DEPENDENCY_ERROR = str(e)
try:
    from . import config
except ImportError:
    config = None

class RAGManager:
    # class manager for rag pipeline
    
    def __init__(self):
        self.embedder = None
        self.vector_store = None
        self.error_message = None
    
    def _ensure_initialized(self):
        """Initialize on first use if not already done"""
        if self.embedder is not None and self.vector_store is not None:
            return True
        
        if not DEPENDENCIES_OK:
            self.error_message = f"Missing dependencies: {DEPENDENCY_ERROR}"
            return False
        
        if config is None:
            self.error_message = "Config not available"
            return False
        
        try:
            # embedding model
            self.embedder = SentenceTransformer(
                model_name_or_path=config.EMBEDDING_MODEL_NAME,
                trust_remote_code=True,
            )
            
            # vector store
            self.vector_store = VectorStore(
                addon_directory=str(config.ADDON_DIR),
                vector_store_directiory=str(config.VECTORSTORE_DIR),
                embedding_backup_directory=str(config.EMBEDDINGS_BACKUP_DIR)
            )
            
            # check if collection exists, create if needed
            if not self._collection_exists():
                self._create_collection()

            return True
        except Exception as e:
            self.error_message = f"Initialization failed: {str(e)}"
            print(f"RAG Manager error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _collection_exists(self) -> bool:
        """Check if collection exists"""
        try:
            self.vector_store.get_collection_info(config.COLLECTION_NAME)
            return True
        except:
            return False
    
    def _create_collection(self):
        self.vector_store.create_collection(
            collection_name=config.COLLECTION_NAME,
            embedding_dimension=config.EMBEDDING_DIMENSION,
            vector_name=config.VECTOR_NAME,
            distance_metric=Distance.COSINE
        )
        
        with open(config.DATASET_JSON, 'r') as f:
            data = json.load(f)
        
        objects = data['objects']
        texts_to_embed = []
        metadata_list = []
        
        for obj in objects:
            try:
                # Read description
                desc_path = Path(obj['description_file'])
                if not desc_path.is_absolute():
                    desc_path = config.ADDON_DIR / desc_path
                with open(desc_path, 'r') as f:
                    description = f.read().strip()
                
                # Read code
                code_path = Path(obj['code_file'])
                if not code_path.is_absolute():
                    code_path = config.ADDON_DIR / code_path
                with open(code_path, 'r') as f:
                    python_code = f.read().strip()
                
                texts_to_embed.append(f"Object description: {description}")
                metadata_list.append({
                    "id": obj['id'],
                    'category': obj['category'],
                    'subcategory': obj['subcategory'],
                    'code': python_code
                })
            except Exception as e:
                print(f"Error processing {obj['id']}: {e}")
        
        # Embed and add in batches
        batch_size = 128
        for i in range(0, len(texts_to_embed), batch_size):
            batch_texts = texts_to_embed[i:i+batch_size]
            batch_metadata = metadata_list[i:i+batch_size]
            
            embeddings = self.embedder.encode(
                sentences=batch_texts,
                precision='float32',
                convert_to_tensor=True,
                show_progress_bar=True,
            )
            
            self.vector_store.add_data(
                collection_name=config.COLLECTION_NAME,
                vector_name=config.VECTOR_NAME,
                embeddings=embeddings,
                metadata_list=batch_metadata
            )
        
        print(f"Database created with {len(texts_to_embed)} objects")
    
    def query(self, prompt: str, k: int = 5) -> Tuple[Optional[List], Optional[str]]:
        if not self._ensure_initialized():
            return None, self.error_message
        
        try:
            # Embed query
            query_embedding = self.embedder.encode(
                prompt,
                precision='float32',
                convert_to_tensor=True,
            )
            
            # Search
            results = self.vector_store.search(
                collection_name=config.COLLECTION_NAME,
                query_embedding=query_embedding,
                k=k
            )
            
            return results, None
            
        except Exception as e:
            return None, f"Query failed: {str(e)}"
    
    def unload(self):
        if self.vector_store:
            self.vector_store.close()
        self.embedder = None
        self.vector_store = None

_rag_instance = None # singleton instance
def get_rag_manager() -> RAGManager:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGManager()
    return _rag_instance