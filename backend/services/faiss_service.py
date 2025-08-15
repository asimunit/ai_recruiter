"""
FAISS service for vector storage and similarity search
"""
import faiss
import numpy as np
import json
import os
from typing import List, Tuple, Dict, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class FAISSService:
    """Service for FAISS vector database operations"""

    def __init__(self):
        self.index = None
        self.metadata = {}
        self.dimension = settings.EMBEDDING_DIMENSION
        self._initialize_index()

    def _initialize_index(self):
        """Initialize or load FAISS index"""
        try:
            if os.path.exists(settings.FAISS_INDEX_PATH) and os.path.exists(
                    settings.FAISS_METADATA_PATH):
                self._load_index()
            else:
                self._create_new_index()

            logger.info(
                f"✅ FAISS index initialized with {self.get_total_vectors()} vectors")

        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {str(e)}")
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index"""
        try:
            # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = {}

            logger.info(
                f"Created new FAISS index with dimension {self.dimension}")
            self._save_index()

        except Exception as e:
            logger.error(f"Failed to create FAISS index: {str(e)}")
            raise RuntimeError(f"Could not create FAISS index: {str(e)}")

    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(settings.FAISS_INDEX_PATH)

            # Load metadata
            with open(settings.FAISS_METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)

            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")

        except Exception as e:
            logger.error(f"Failed to load FAISS index: {str(e)}")
            raise RuntimeError(f"Could not load FAISS index: {str(e)}")

    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, settings.FAISS_INDEX_PATH)

            # Save metadata
            with open(settings.FAISS_METADATA_PATH, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)

            logger.info("FAISS index and metadata saved successfully")

        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")
            raise RuntimeError(f"Could not save FAISS index: {str(e)}")

    def add_vector(self, resume_id: str, embedding: np.ndarray,
                   resume_data: dict):
        """
        Add a single vector to the index

        Args:
            resume_id (str): Unique resume identifier
            embedding (np.ndarray): Embedding vector
            resume_data (dict): Resume metadata
        """
        try:
            # Ensure embedding is the right shape and normalized
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)

            # Normalize for cosine similarity
            faiss.normalize_L2(embedding)

            # Add to index
            self.index.add(embedding.astype(np.float32))

            # Store metadata
            vector_id = self.index.ntotal - 1  # Index of the added vector
            self.metadata[str(vector_id)] = {
                'resume_id': resume_id,
                'filename': resume_data.get('filename', ''),
                'skills': resume_data.get('skills', []),
                'experience_years': resume_data.get('experience_years'),
                'education': resume_data.get('education', []),
                'sections': resume_data.get('sections', {}),
                'added_at': str(resume_data.get('created_at', ''))
            }

            # Save changes
            self._save_index()

            logger.info(
                f"Added vector for resume {resume_id} (index: {vector_id})")

        except Exception as e:
            logger.error(f"Failed to add vector: {str(e)}")
            raise RuntimeError(f"Could not add vector to index: {str(e)}")

    def add_vectors_batch(self, resume_data_list: List[Dict]):
        """
        Add multiple vectors to the index in batch

        Args:
            resume_data_list (List[Dict]): List of resume data with embeddings
        """
        try:
            embeddings = []
            metadata_batch = {}

            for data in resume_data_list:
                embedding = data['embedding']
                if embedding.ndim == 1:
                    embedding = embedding.reshape(1, -1)
                embeddings.append(embedding)

                # Prepare metadata
                vector_id = self.index.ntotal + len(embeddings) - 1
                metadata_batch[str(vector_id)] = {
                    'resume_id': data['resume_id'],
                    'filename': data.get('filename', ''),
                    'skills': data.get('skills', []),
                    'experience_years': data.get('experience_years'),
                    'education': data.get('education', []),
                    'sections': data.get('sections', {}),
                    'added_at': str(data.get('created_at', ''))
                }

            # Combine embeddings and normalize
            embeddings_array = np.vstack(embeddings).astype(np.float32)
            faiss.normalize_L2(embeddings_array)

            # Add to index
            self.index.add(embeddings_array)

            # Update metadata
            self.metadata.update(metadata_batch)

            # Save changes
            self._save_index()

            logger.info(f"Added {len(resume_data_list)} vectors to index")

        except Exception as e:
            logger.error(f"Failed to add vectors batch: {str(e)}")
            raise RuntimeError(f"Could not add vectors to index: {str(e)}")

    def search(self, query_embedding: np.ndarray, top_k: int = 10,
               threshold: float = 0.7) -> List[Dict]:
        """
        Search for similar vectors

        Args:
            query_embedding (np.ndarray): Query embedding vector
            top_k (int): Number of top results to return
            threshold (float): Similarity threshold (0-1)

        Returns:
            List[Dict]: List of matching results with metadata
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("FAISS index is empty")
                return []

            # Prepare query embedding
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)

            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)

            # Search
            similarities, indices = self.index.search(
                query_embedding.astype(np.float32),
                min(top_k, self.index.ntotal)
            )

            # Process results
            results = []
            for i, (similarity, idx) in enumerate(
                    zip(similarities[0], indices[0])):
                if similarity >= threshold and str(idx) in self.metadata:
                    result = {
                        'similarity_score': float(similarity),
                        'index': int(idx),
                        **self.metadata[str(idx)]
                    }
                    results.append(result)

            logger.info(
                f"Found {len(results)} matches above threshold {threshold}")
            return results

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise RuntimeError(f"Could not perform search: {str(e)}")

    def get_vector_by_resume_id(self, resume_id: str) -> Optional[
        Tuple[np.ndarray, Dict]]:
        """
        Get vector and metadata by resume ID

        Args:
            resume_id (str): Resume identifier

        Returns:
            Optional[Tuple[np.ndarray, Dict]]: Vector and metadata if found
        """
        try:
            for idx_str, metadata in self.metadata.items():
                if metadata.get('resume_id') == resume_id:
                    idx = int(idx_str)
                    vector = self.index.reconstruct(idx)
                    return vector, metadata

            return None

        except Exception as e:
            logger.error(f"Failed to get vector by resume ID: {str(e)}")
            return None

    def delete_vector(self, resume_id: str) -> bool:
        """
        Delete vector by resume ID (not directly supported by FAISS, requires rebuild)

        Args:
            resume_id (str): Resume identifier

        Returns:
            bool: Success status
        """
        logger.warning(
            "Vector deletion requires index rebuild - not implemented in this version")
        return False

    def get_total_vectors(self) -> int:
        """Get total number of vectors in the index"""
        return self.index.ntotal if self.index else 0

    def get_index_info(self) -> Dict:
        """Get information about the FAISS index"""
        return {
            'total_vectors': self.get_total_vectors(),
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else 'None',
            'metadata_count': len(self.metadata),
            'index_file_exists': os.path.exists(settings.FAISS_INDEX_PATH),
            'metadata_file_exists': os.path.exists(
                settings.FAISS_METADATA_PATH)
        }

    def rebuild_index(self):
        """Rebuild the entire index (useful for maintenance)"""
        try:
            if not self.metadata:
                logger.info("No metadata found, creating fresh index")
                self._create_new_index()
                return

            # This would require re-extracting embeddings from stored resume data
            # For now, just recreate empty index
            self._create_new_index()
            logger.info("Index rebuilt successfully")

        except Exception as e:
            logger.error(f"Failed to rebuild index: {str(e)}")
            raise RuntimeError(f"Could not rebuild index: {str(e)}")


# Global FAISS service instance
faiss_service = FAISSService()


def get_faiss_service() -> FAISSService:
    """Get the global FAISS service instance"""
    return faiss_service