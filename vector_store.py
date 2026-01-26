import os 
import uuid
import json
import pickle
from pathlib import Path
from typing import Any, Optional, Union, List, Dict

from qdrant_client import QdrantClient
from datapizza.vectorstores.qdrant import QdrantVectorstore
from datapizza.core.vectorstore import Distance, VectorConfig
from datapizza.type import EmbeddingFormat, Chunk, DenseEmbedding

class VectorStore:
    def __init__(
        self, 
        addon_directory: str,
        vector_store_directiory: str,
        embedding_backup_directory: str
    ):
        """Init the vector store with automatic backup support."""
        
        self.addon_directory = addon_directory
        self.vectorstore_path = vector_store_directiory 
        self.embeddings_backup_path = embedding_backup_directory
                
        qdrant_client = QdrantClient(
            path=str(self.vectorstore_path),
            force_disable_check_same_thread=True 
        )

        self.vectorstore = QdrantVectorstore.__new__(QdrantVectorstore)
        self.vectorstore.client = qdrant_client
        self.vectorstore.host = None
        self.vectorstore.port = None
        self.vectorstore.api_key = None
        self.vectorstore.location = None
        self.vectorstore.kwargs = {}

    def _save_collection_metadata(
        self,
        collection_name: str,
        embedding_dimension: int,
        vector_name: str,
        distance_metric: Distance
    ):
        """ Save collection configuration to disk """
        collection_dir = Path(self.embeddings_backup_path) / collection_name
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "collection_name": collection_name,
            "embedding_dimension": embedding_dimension,
            "vector_name": vector_name,
            "distance_metric": distance_metric.name
        }
        
        metadata_file = collection_dir / "collection_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _save_embeddings_to_disk(self, collection_name: str, embeddings_data: List[Dict]):
        # append embeddings to the backup file
        collection_dir = Path(self.embeddings_backup_path) / collection_name
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        embeddings_file = collection_dir / "embeddings.pkl"
        
        existing_data = []
        if embeddings_file.exists():
            with open(embeddings_file, 'rb') as f:
                existing_data = pickle.load(f)
        
        existing_data.extend(embeddings_data)
        with open(embeddings_file, 'wb') as f:
            pickle.dump(existing_data, f)

    def _list_backed_up_collections(self) -> List[str]:
        # list all collections that have backups
        backup_path = Path(self.embeddings_backup_path)
        if not backup_path.exists():
            return []
        
        return [d.name for d in backup_path.iterdir() if d.is_dir()]

    def create_collection(
        self,
        collection_name: str,
        embedding_dimension: int,
        vector_name: str,
        distance_metric: Distance = Distance.COSINE
    ):
        vector_config = [
            VectorConfig(
                name = vector_name,
                dimensions = embedding_dimension,
                format = EmbeddingFormat.DENSE,
                distance = distance_metric
            )
        ]

        self.vectorstore.create_collection(
            collection_name = collection_name,
            vector_config = vector_config
        )

        self._save_collection_metadata(
            collection_name = collection_name,
            embedding_dimension = embedding_dimension,
            vector_name = vector_name,
            distance_metric = distance_metric
        )

        print(f"Collection {collection_name} created successfully")
        print(f"Vector name: {vector_name}")
        print(f"Embedding dimension: {embedding_dimension}")

    def add_data(
    self,
    embeddings,
    collection_name: str,
    vector_name: str,
    metadata_list: Optional[Union[List[Dict], Dict]] = None,
    auto_backup: bool = True
    ):
        # Ensure embeddings is 2D: (batch_size, embedding_dim)
        if len(embeddings.shape) == 1:
            embeddings = embeddings.unsqueeze(0)
        
        # Verify batch sizes match
        num_embeddings = embeddings.shape[0]
        num_metadata = len(metadata_list)
        
        if num_embeddings != num_metadata:
            raise ValueError(f"Mismatch: {num_embeddings} embeddings but {num_metadata} metadata entries")
        
        chunks = []
        embeddings_to_save = []
        
        # Explicit iteration using index
        for i in range(num_embeddings):
            embedding = embeddings[i]  # Extract single embedding tensor
            metadata_dict = metadata_list[i]
            chunk_id = str(uuid.uuid4())
            
            chunk = Chunk(
                id=chunk_id,
                text="",
                metadata=metadata_dict,
                embeddings=[
                    DenseEmbedding(
                        name=vector_name,
                        vector=embedding.flatten().tolist()
                    )
                ]
            )
            chunks.append(chunk)
            
            if auto_backup:
                embeddings_to_save.append({
                    "id": chunk_id,
                    "embedding": embedding,
                    "metadata": metadata_dict
                })
        
        self.vectorstore.add(
            chunk=chunks,
            collection_name=collection_name
        )
        
        if auto_backup:
            self._save_embeddings_to_disk(
                collection_name=collection_name,
                embeddings_data=embeddings_to_save
            )
        
        print(f"Added {len(chunks)} chunks to {collection_name}.")
    
    def search(
        self,
        query_embedding,
        collection_name: str,
        k: int = 10,
        query_filter = None,
        with_vectors: bool = True,
        metadata_filter: Optional[Dict[str, Any]] = None
    ):
        # search for similar vectors
        query_vector = query_embedding.flatten().tolist()

        results = self.vectorstore.search(
            collection_name=collection_name,
            query_vector=query_vector,
            k=k,
            with_vectors = with_vectors,
            query_filter = query_filter
        )

        return results
    
    def rebuild_from_disk(self):
        # rebuild all collections from backed up embeddings on disk.
        
        backup_path = Path(self.embeddings_backup_path)
        if not backup_path.exists():
            print("No backup found.")
            return
        
        # get all collection directories
        collection_dirs = [d for d in backup_path.iterdir() if d.is_dir()]
        if not collection_dirs:
            print("No collections to rebuild.")
            return
               
        for collection_dir in collection_dirs:
            collection_name = collection_dir.name
            metadata_file = collection_dir / "collection_metadata.json"
            if not metadata_file.exists():
                print(f"Skipping {collection_name}: no metadata found")
                continue
            
            with open(metadata_file, 'r') as f:
                coll_metadata = json.load(f)
            
            # recreate collection
            self.create_collection(
                collection_name=collection_name,
                embedding_dimension=coll_metadata['embedding_dimension'],
                vector_name=coll_metadata['vector_name'],
                distance_metric=Distance[coll_metadata['distance_metric']]
            )
            
            # load and add all embeddings
            embeddings_file = collection_dir / "embeddings.pkl"
            if embeddings_file.exists():
                with open(embeddings_file, 'rb') as f:
                    saved_data = pickle.load(f)
                
                print(f"Loading {len(saved_data)} embeddings...")
                
                for item in saved_data:
                    self.add_data(
                        collection_name=collection_name,
                        vector_name=coll_metadata['vector_name'],
                        embeddings=item['embedding'],
                        metadata_list=item['metadata'],
                        auto_backup=False  # do nott re-backup during rebuild
                    )
                
                print(f"Rebuilt {collection_name} with {len(saved_data)} embeddings")
            else:
                print(f"No embeddings file found for {collection_name}")
        
        print("rebuild ok.")
    
    def get_collection_info(self, collection_name: str):
        """Get information about a collection including vector names"""
        collection_info = self.vectorstore.client.get_collection(collection_name)
        print(f"\nCollection: {collection_name}")
        print(f"Vectors config: {collection_info.config.params.vectors}")
        return collection_info
            
    def close(self):
        if hasattr(self.vectorstore.client, 'close'):
            self.vectorstore.client.close()