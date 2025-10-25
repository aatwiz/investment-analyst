"""
Embedding service for generating and managing vector embeddings.
Inspired by open-notebook's embedding workflow, adapted for PostgreSQL + pgvector.
"""
import os
from typing import List, Optional

import openai
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.document import DocumentEmbedding
from backend.utils.text_utils import split_text

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Embedding configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
CHUNK_SIZE = 500  # Characters per chunk (similar to open-notebook)
CHUNK_OVERLAP = 50  # Overlap between chunks


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text string using OpenAI.
    
    Args:
        text: The text to embed
        
    Returns:
        List of floats representing the embedding vector
        
    Raises:
        Exception: If embedding generation fails
    """
    try:
        response = await openai.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        logger.debug(f"Generated embedding with {len(embedding)} dimensions for text of length {len(text)}")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single API call.
    More efficient than individual calls.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    try:
        response = await openai.embeddings.create(
            input=texts,
            model=EMBEDDING_MODEL
        )
        embeddings = [item.embedding for item in response.data]
        logger.info(f"Generated {len(embeddings)} embeddings in batch")
        return embeddings
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise


async def embed_document_chunks(
    session: AsyncSession,
    document_id: int,
    full_text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> int:
    """
    Split document into chunks and generate embeddings for each.
    Similar to open-notebook's vectorization process.
    
    Args:
        session: Database session
        document_id: ID of the document to embed
        full_text: Full text content of the document
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between consecutive chunks
        
    Returns:
        Number of chunks created
    """
    try:
        # Split text into chunks
        chunks = split_text(full_text, chunk_size, chunk_overlap)
        logger.info(f"Split document {document_id} into {len(chunks)} chunks")
        
        if not chunks:
            logger.warning(f"No chunks generated for document {document_id}")
            return 0
        
        # Generate embeddings for all chunks
        embeddings = await generate_embeddings_batch(chunks)
        
        # Create DocumentEmbedding records
        embedding_records = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            embedding_record = DocumentEmbedding(
                document_id=document_id,
                content=chunk,
                embedding=embedding,
                embedding_model=EMBEDDING_MODEL,
                embedding_dimensions=EMBEDDING_DIMENSIONS
            )
            embedding_records.append(embedding_record)
        
        # Bulk insert all embeddings
        session.add_all(embedding_records)
        await session.commit()
        
        logger.info(f"Created {len(embedding_records)} embeddings for document {document_id}")
        return len(embedding_records)
        
    except Exception as e:
        logger.error(f"Error embedding document chunks: {e}")
        await session.rollback()
        raise


async def vector_search(
    session: AsyncSession,
    query_text: str,
    limit: int = 10,
    minimum_similarity: float = 0.2,
    document_ids: Optional[List[int]] = None
) -> List[dict]:
    """
    Perform semantic vector search using pgvector.
    Inspired by open-notebook's vector_search function.
    
    Args:
        session: Database session
        query_text: Text to search for
        limit: Maximum number of results
        minimum_similarity: Minimum cosine similarity score (0.0 to 1.0)
        document_ids: Optional list of document IDs to search within
        
    Returns:
        List of dicts containing:
            - id: Embedding ID
            - content: Text content
            - document_id: Source document ID
            - similarity: Similarity score (1.0 - cosine distance)
    """
    try:
        # Generate embedding for query
        query_embedding = await generate_embedding(query_text)
        logger.debug(f"Generated query embedding for: '{query_text[:50]}...'")
        
        # Build query with pgvector cosine distance operator (<->)
        # Note: cosine distance = 1 - cosine similarity
        # So similarity = 1 - distance
        query = select(
            DocumentEmbedding.id,
            DocumentEmbedding.content,
            DocumentEmbedding.document_id,
            DocumentEmbedding.embedding_model,
            (1 - DocumentEmbedding.embedding.cosine_distance(query_embedding)).label("similarity")
        )
        
        # Filter by document IDs if provided
        if document_ids:
            query = query.where(DocumentEmbedding.document_id.in_(document_ids))
        
        # Filter by minimum similarity
        query = query.where(
            (1 - DocumentEmbedding.embedding.cosine_distance(query_embedding)) >= minimum_similarity
        )
        
        # Order by similarity (highest first) and limit
        query = query.order_by((1 - DocumentEmbedding.embedding.cosine_distance(query_embedding)).desc())
        query = query.limit(limit)
        
        # Execute query
        result = await session.execute(query)
        rows = result.all()
        
        # Format results
        results = [
            {
                "id": row.id,
                "content": row.content,
                "document_id": row.document_id,
                "embedding_model": row.embedding_model,
                "similarity": float(row.similarity)
            }
            for row in rows
        ]
        
        logger.info(f"Vector search returned {len(results)} results for query: '{query_text[:50]}...'")
        return results
        
    except Exception as e:
        logger.error(f"Error performing vector search: {e}")
        raise


async def rebuild_document_embeddings(
    session: AsyncSession,
    document_id: int,
    full_text: str
) -> int:
    """
    Rebuild embeddings for a document (delete old ones and create new).
    Useful when changing embedding models or fixing corrupted embeddings.
    
    Args:
        session: Database session
        document_id: ID of the document
        full_text: Full text content
        
    Returns:
        Number of new embeddings created
    """
    try:
        # Delete existing embeddings
        await session.execute(
            select(DocumentEmbedding).where(DocumentEmbedding.document_id == document_id)
        )
        existing = (await session.execute(
            select(DocumentEmbedding).where(DocumentEmbedding.document_id == document_id)
        )).scalars().all()
        
        for embedding in existing:
            await session.delete(embedding)
        
        await session.commit()
        logger.info(f"Deleted {len(existing)} old embeddings for document {document_id}")
        
        # Create new embeddings
        count = await embed_document_chunks(session, document_id, full_text)
        logger.info(f"Rebuilt {count} embeddings for document {document_id}")
        return count
        
    except Exception as e:
        logger.error(f"Error rebuilding embeddings: {e}")
        await session.rollback()
        raise
