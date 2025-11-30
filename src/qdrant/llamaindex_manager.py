"""Production-grade LlamaIndex integration for deployment logging.

This module provides a robust RAG pipeline using LlamaIndex for:
- Automatic document parsing and chunking
- Mistral AI embeddings via LlamaIndex wrapper
- Qdrant vector storage via LlamaIndex integration
- Advanced semantic search with metadata filtering
- Automatic source citation and response synthesis
"""

import os
import time
from typing import Any, Optional

# Load environment variables BEFORE checking them
from dotenv import load_dotenv
load_dotenv()

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core.vector_stores import (
    ExactMatchFilter,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Environment variable validation
mistral_api_key = os.getenv("MISTRAL_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

# Check for required environment variables
_logging_enabled = True
_missing_vars = []

if not mistral_api_key:
    _missing_vars.append("MISTRAL_API_KEY")
if not qdrant_url:
    _missing_vars.append("QDRANT_URL")
if not qdrant_api_key:
    _missing_vars.append("QDRANT_API_KEY")

if _missing_vars:
    _logging_enabled = False
    # Use stderr for warnings to avoid breaking STDIO MCP protocol
    import sys
    print(f"[WARN] Missing environment variables: {', '.join(_missing_vars)}", file=sys.stderr)
    print(
        "[WARN] Deployment logging to Qdrant is disabled. Deployments will continue normally.",
        file=sys.stderr
    )

# Initialize Qdrant client
qdrant_client = (
    QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    if _logging_enabled
    else None
)

# Initialize LlamaIndex components (only if logging enabled)
if _logging_enabled:
    # Configure Mistral embeddings via LlamaIndex
    embed_model = MistralAIEmbedding(
        api_key=mistral_api_key,
        model_name="mistral-embed",  # 1024 dimensions
    )

    # Set global LlamaIndex settings
    Settings.embed_model = embed_model
    Settings.chunk_size = 512
    Settings.chunk_overlap = 50

    # Node parser for text chunking
    node_parser = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50,
    )
else:
    embed_model = None
    node_parser = None


class FleetLogIndex:
    """Production-grade LlamaIndex wrapper for fleet deployment logs.

    This class provides a robust interface for:
    - Logging deployment events as LlamaIndex Documents
    - Automatic embedding with Mistral AI
    - Storage in Qdrant via LlamaIndex
    - Advanced semantic search with metadata filtering
    - Source citation and response synthesis
    """

    def __init__(self, collection_name: str = "fleet_deployment_logs"):
        """Initialize the fleet log index.

        Args:
            collection_name: Name of the Qdrant collection
        """
        self.collection_name = collection_name
        self.index: Optional[VectorStoreIndex] = None

        if not _logging_enabled:
            return

        try:
            # Ensure collection exists
            self._ensure_collection_exists()

            # Create Qdrant vector store via LlamaIndex
            vector_store = QdrantVectorStore(
                client=qdrant_client,
                collection_name=collection_name,
            )

            # Create storage context
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store
            )

            # Create or load index
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    embed_model=embed_model,
                )
            except Exception:
                # Create new index if doesn't exist
                self.index = VectorStoreIndex(
                    nodes=[],
                    storage_context=storage_context,
                    embed_model=embed_model,
                )

        except Exception as e:
            print(f"[WARN] Failed to initialize LlamaIndex: {e}")
            self.index = None

    def _ensure_collection_exists(self):
        """Ensure Qdrant collection exists with proper configuration."""
        if not qdrant_client:
            return

        try:
            from qdrant_client.models import PayloadSchemaType
            
            # Check if collection exists
            collections = qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                # Create collection with 1024 dimensions (Mistral embed)
                qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1024,  # Mistral embed dimensions
                        distance=Distance.COSINE,
                    ),
                )
                print(f"[OK] Created Qdrant collection: {self.collection_name}")
            
            # Create payload indexes for metadata filtering
            indexes_to_create = {
                "sandbox_name": PayloadSchemaType.KEYWORD,
                "event_type": PayloadSchemaType.KEYWORD,
                "job_id": PayloadSchemaType.KEYWORD,
                "repo_url": PayloadSchemaType.KEYWORD,
                "return_code": PayloadSchemaType.INTEGER,
                "timestamp": PayloadSchemaType.FLOAT,
                "has_error": PayloadSchemaType.BOOL,
            }
            
            for field_name, field_type in indexes_to_create.items():
                try:
                    qdrant_client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=field_type,
                    )
                    print(f"[OK] Created index: {self.collection_name}.{field_name}")
                except Exception as e:
                    # Index might already exist
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        pass  # Silently ignore
                    else:
                        print(f"[WARN] Could not create index {field_name}: {e}")

        except Exception as e:
            print(f"[WARN] Failed to ensure collection exists: {e}")

    def log_deployment_event(
        self,
        event_type: str,
        sandbox_name: str,
        job_id: str,
        repo_url: str = "",
        stdout: str = "",
        stderr: str = "",
        return_code: Optional[int] = None,
        deploy_time: Optional[float] = None,
        preview_url: str = "",
    ) -> bool:
        """Log a deployment event using LlamaIndex Documents.

        Args:
            event_type: Type of event (START, SUCCESS, FAILURE)
            sandbox_name: Name of the sandbox
            job_id: Unique job identifier
            repo_url: Repository URL being deployed
            stdout: Standard output
            stderr: Standard error
            return_code: Exit code (None for in-progress)
            deploy_time: Deployment time in seconds
            preview_url: Preview URL (for success events)

        Returns:
            True if logging succeeded, False otherwise
        """
        if not _logging_enabled or not self.index:
            return False

        try:
            # Build document text
            text_parts = [f"Event: {event_type}"]

            if repo_url:
                text_parts.append(f"Repository: {repo_url}")

            if stdout:
                text_parts.append(f"Output: {stdout}")

            if stderr:
                text_parts.append(f"Error: {stderr}")

            if preview_url:
                text_parts.append(f"Preview URL: {preview_url}")

            if deploy_time is not None:
                text_parts.append(f"Deploy Time: {deploy_time:.2f}s")

            text = "\n".join(text_parts)

            # Create LlamaIndex Document with rich metadata
            doc = Document(
                text=text,
                metadata={
                    "event_type": event_type,
                    "sandbox_name": sandbox_name,
                    "job_id": job_id,
                    "repo_url": repo_url,
                    "return_code": return_code if return_code is not None else -1,
                    "timestamp": time.time(),
                    "deploy_time": deploy_time if deploy_time is not None else 0.0,
                    "preview_url": preview_url,
                    "has_error": len(stderr) > 0,
                },
                excluded_llm_metadata_keys=[
                    "timestamp",
                    "deploy_time",
                ],  # Don't send to LLM
                excluded_embed_metadata_keys=[],  # Include all in embeddings
            )

            # Insert document into index (automatic embedding + storage)
            self.index.insert(doc)

            return True

        except Exception as e:
            print(f"[WARN] Failed to log deployment event: {e}")
            return False

    def search(
        self,
        query: str,
        sandbox_name: Optional[str] = None,
        event_type: Optional[str] = None,
        return_code: Optional[int] = None,
        time_hours: Optional[int] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search deployment logs using semantic similarity.

        Args:
            query: Natural language search query
            sandbox_name: Filter by sandbox name
            event_type: Filter by event type (START, SUCCESS, FAILURE)
            return_code: Filter by return code (0=success, 1=failure, -1=in-progress)
            time_hours: Filter by last N hours
            limit: Maximum number of results

        Returns:
            List of search results with metadata and source citations
        """
        if not _logging_enabled or not self.index:
            return []

        try:
            # Build metadata filters
            filters = []

            if sandbox_name:
                filters.append(
                    MetadataFilter(key="sandbox_name", value=sandbox_name)
                )

            if event_type:
                filters.append(MetadataFilter(key="event_type", value=event_type))

            if return_code is not None:
                filters.append(
                    MetadataFilter(key="return_code", value=return_code)
                )

            if time_hours:
                since_timestamp = time.time() - (time_hours * 3600)
                filters.append(
                    MetadataFilter(
                        key="timestamp",
                        value=since_timestamp,
                        operator=">=",
                    )
                )

            # Create retriever with filters
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=limit,
                filters=MetadataFilters(filters=filters) if filters else None,
            )

            # Retrieve nodes
            nodes: list[NodeWithScore] = retriever.retrieve(query)

            # Format results
            results = []
            for node in nodes:
                metadata = node.node.metadata
                results.append(
                    {
                        "relevance_score": node.score,
                        "text": node.node.get_content(),
                        "event_type": metadata.get("event_type", ""),
                        "sandbox_name": metadata.get("sandbox_name", ""),
                        "job_id": metadata.get("job_id", ""),
                        "repo_url": metadata.get("repo_url", ""),
                        "return_code": metadata.get("return_code", -1),
                        "timestamp": metadata.get("timestamp", 0),
                        "deploy_time": metadata.get("deploy_time", 0.0),
                        "preview_url": metadata.get("preview_url", ""),
                        "has_error": metadata.get("has_error", False),
                        "formatted_time": time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(metadata.get("timestamp", 0)),
                        ),
                    }
                )

            return results

        except Exception as e:
            print(f"[WARN] Search failed: {e}")
            return []

    def suggest_fixes(
        self,
        problem_description: str,
        sandbox_name: Optional[str] = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Suggest fixes from successful deployments.

        Args:
            problem_description: Description of the problem
            sandbox_name: Optional sandbox name for context
            limit: Maximum number of suggestions

        Returns:
            List of successful deployment events that might help
        """
        # Search for successful deployments (return_code=0)
        results = self.search(
            query=problem_description,
            sandbox_name=sandbox_name,
            return_code=0,  # Only successful deployments
            limit=limit * 2,  # Get more to deduplicate
        )

        # Deduplicate by repo_url and format as suggestions
        seen_repos = set()
        suggestions = []

        for result in results:
            repo_url = result.get("repo_url", "")
            if repo_url and repo_url not in seen_repos:
                seen_repos.add(repo_url)
                suggestions.append(
                    {
                        "repo_url": repo_url,
                        "sandbox_name": result["sandbox_name"],
                        "deploy_time": result["deploy_time"],
                        "preview_url": result["preview_url"],
                        "relevance_score": result["relevance_score"],
                        "timestamp": result["formatted_time"],
                        "success_rate": 1.0,  # Only successful deployments
                    }
                )

            if len(suggestions) >= limit:
                break

        return suggestions


# Global index instance
_fleet_index: Optional[FleetLogIndex] = None


def get_fleet_index() -> FleetLogIndex:
    """Get or create the global fleet log index.

    Returns:
        FleetLogIndex instance
    """
    global _fleet_index
    if _fleet_index is None:
        _fleet_index = FleetLogIndex()
    return _fleet_index


# Convenience functions for backward compatibility
async def log_blaxel_operation(
    sandbox_name: str,
    command: str,
    job_id: str,
    stdout: str = "",
    stderr: str = "",
    return_code: Optional[int] = None,
    requested_by: Optional[str] = None,
) -> None:
    """Log a Blaxel operation (backward compatible interface).

    Args:
        sandbox_name: Name of the sandbox
        command: Command or operation description
        job_id: Unique job identifier
        stdout: Standard output
        stderr: Standard error
        return_code: Exit code
        requested_by: User who requested (unused)
    """
    if not _logging_enabled:
        return

    try:
        index = get_fleet_index()

        # Parse command to extract event type and repo URL
        event_type = "COMMAND"
        repo_url = ""

        if "DEPLOYMENT_START:" in command:
            event_type = "START"
            repo_url = command.split("DEPLOYMENT_START:")[-1].strip()
        elif "DEPLOYMENT_SUCCESS:" in command:
            event_type = "SUCCESS"
            repo_url = command.split("DEPLOYMENT_SUCCESS:")[-1].strip()
        elif "DEPLOYMENT_FAILURE:" in command:
            event_type = "FAILURE"
            repo_url = command.split("DEPLOYMENT_FAILURE:")[-1].strip()

        # Extract deploy time and preview URL from stdout
        deploy_time = None
        preview_url = ""

        if "Time:" in stdout:
            try:
                time_str = stdout.split("Time:")[-1].split("s")[0].strip()
                deploy_time = float(time_str)
            except Exception:
                pass

        if "URL:" in stdout:
            try:
                preview_url = stdout.split("URL:")[-1].split()[0].strip()
            except Exception:
                pass

        # Log the event
        index.log_deployment_event(
            event_type=event_type,
            sandbox_name=sandbox_name,
            job_id=job_id,
            repo_url=repo_url,
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
            deploy_time=deploy_time,
            preview_url=preview_url,
        )

    except Exception as e:
        print(f"[WARN] Failed to log operation: {e}")
