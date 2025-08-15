"""
Embedding service using mxbai model from Hugging Face
"""
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
import torch
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using mxbai model"""

    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the mxbai embedding model with fallback options"""

        # List of models to try in order of preference
        model_options = [
            settings.EMBEDDING_MODEL,  # Primary: mxbai-embed-large-v1
            "sentence-transformers/all-MiniLM-L6-v2",  # Fallback 1: Lightweight
            "sentence-transformers/all-mpnet-base-v2",  # Fallback 2: Good quality
            "sentence-transformers/paraphrase-MiniLM-L6-v2"  # Fallback 3: Fast
        ]

        for model_name in model_options:
            try:
                logger.info(f"Attempting to load embedding model: {model_name}")

                # Try to load the model
                self.model = SentenceTransformer(
                    model_name,
                    device=self.device,
                    trust_remote_code=True  # Allow loading newer model formats
                )

                # Test the model with a simple sentence
                test_embedding = self.model.encode("test sentence")
                actual_dimension = len(test_embedding)

                logger.info(f"✅ Embedding model loaded successfully: {model_name}")
                logger.info(f"📐 Model dimension: {actual_dimension} (device: {self.device})")

                # Update settings with actual dimension if different
                if actual_dimension != settings.EMBEDDING_DIMENSION:
                    logger.warning(f"⚠️ Model dimension ({actual_dimension}) differs from config ({settings.EMBEDDING_DIMENSION})")
                    settings.EMBEDDING_DIMENSION = actual_dimension

                # Store the successful model name
                settings.EMBEDDING_MODEL = model_name
                return

            except Exception as e:
                logger.warning(f"⚠️ Failed to load {model_name}: {str(e)}")
                if model_name == model_options[-1]:  # Last option failed
                    logger.error(f"❌ All embedding models failed to load")
                    raise RuntimeError(f"Could not initialize any embedding model. Last error: {str(e)}")
                continue

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text

        Args:
            text (str): Input text

        Returns:
            np.ndarray: Embedding vector
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        try:
            # Clean and truncate text if necessary
            cleaned_text = self._preprocess_text(text)

            # Generate embedding
            embedding = self.model.encode(
                cleaned_text,
                convert_to_numpy=True,
                normalize_embeddings=True
            )

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")

    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts

        Args:
            texts (List[str]): List of input texts

        Returns:
            np.ndarray: Array of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        try:
            # Clean and preprocess texts
            cleaned_texts = [self._preprocess_text(text) for text in texts]

            # Generate embeddings in batch
            embeddings = self.model.encode(
                cleaned_texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=len(texts) > 10
            )

            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding generation

        Args:
            text (str): Raw text

        Returns:
            str: Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""

        # Basic cleaning
        text = text.strip()
        text = " ".join(text.split())  # Remove extra whitespace

        # Truncate if too long (model has max sequence length)
        if len(text) > settings.MAX_SEQUENCE_LENGTH * 4:  # Rough character estimate
            text = text[:settings.MAX_SEQUENCE_LENGTH * 4]
            logger.warning("Text truncated due to length limit")

        return text

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1 (np.ndarray): First embedding
            embedding2 (np.ndarray): Second embedding

        Returns:
            float: Cosine similarity score (0-1)
        """
        try:
            # Ensure embeddings are normalized
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            # Compute cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)

            # Ensure result is between 0 and 1
            similarity = max(0.0, min(1.0, float(similarity)))

            return similarity

        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return 0.0

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model

        Returns:
            dict: Model information
        """
        if not self.model:
            return {"status": "not_loaded"}

        return {
            "model_name": settings.EMBEDDING_MODEL,
            "device": self.device,
            "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown'),
            "embedding_dimension": settings.EMBEDDING_DIMENSION,
            "status": "loaded"
        }

# Global embedding service instance
embedding_service = EmbeddingService()

def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance"""
    return embedding_service