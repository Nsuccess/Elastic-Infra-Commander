"""LlamaIndex-powered MCP tools for fleet deployment search.

Production-grade semantic search and fix suggestions using LlamaIndex RAG pipeline.
"""

import weave
from mcp.server.fastmcp import Context
from typing import Annotated
from typing_extensions import TypedDict

from src.server import mcp
from .llamaindex_manager import get_fleet_index


class SearchResult(TypedDict):
    """Search result with metadata and source citation."""

    relevance_score: float
    text: str
    event_type: str
    sandbox_name: str
    job_id: str
    repo_url: str
    return_code: int
    timestamp: float
    deploy_time: float
    preview_url: str
    has_error: bool
    formatted_time: str


class SearchResponse(TypedDict):
    """Response from fleet_search_logs."""

    query: str
    total_found: int
    results: list[SearchResult]
    filters_applied: dict


class SuggestionResult(TypedDict):
    """Fix suggestion from successful deployments."""

    repo_url: str
    sandbox_name: str
    deploy_time: float
    preview_url: str
    relevance_score: float
    timestamp: str
    success_rate: float


class SuggestResponse(TypedDict):
    """Response from fleet_suggest_fix."""

    context: str
    sandbox_name: str | None
    total_suggestions: int
    suggestions: list[SuggestionResult]


@mcp.tool(
    name="fleet_search_logs",
    description=(
        "[SEARCH] **LlamaIndex-Powered Semantic Search** across fleet deployment history.\n\n"
        "Uses production-grade RAG pipeline with:\n"
        "- Mistral AI embeddings (1024 dimensions)\n"
        "- Qdrant vector storage\n"
        "- Automatic source citation\n"
        "- Advanced metadata filtering\n\n"
        "**Search Capabilities:**\n"
        "- Natural language queries: 'npm build errors', 'nginx startup failures'\n"
        "- Filter by sandbox, event type, success/failure, time range\n"
        "- Relevance-ranked results with full context\n"
        "- Automatic source attribution (sandbox + timestamp)\n\n"
        "**Parameters:**\n"
        "- query (str, required): Natural language search query\n"
        "- sandbox_name (str, optional): Filter by specific sandbox\n"
        "- event_type (str, optional): Filter by START | SUCCESS | FAILURE\n"
        "- return_code (int, optional): Filter by 0 (success) | 1 (failure) | -1 (in-progress)\n"
        "- time_hours (int, optional): Filter by last N hours\n"
        "- limit (int, optional): Max results (default: 10)\n\n"
        "**Returns:**\n"
        "- Relevance-ranked results with full metadata\n"
        "- Source citations (sandbox, timestamp, job_id)\n"
        "- Event details (repo, deploy time, preview URL)\n\n"
        "**Examples:**\n"
        "- 'Find npm build failures in last 6 hours'\n"
        "- 'Show successful deployments to fleet-game-abc'\n"
        "- 'Search for nginx startup errors'\n"
        "- 'Find all deployments of github.com/user/repo'"
    ),
)
@weave.op()
def fleet_search_logs(
    query: Annotated[str, "Natural language search query"],
    sandbox_name: Annotated[str | None, "Filter by sandbox name"] = None,
    event_type: Annotated[
        str | None, "Filter by event type: START | SUCCESS | FAILURE"
    ] = None,
    return_code: Annotated[
        int | None, "Filter by return code: 0 (success) | 1 (failure) | -1 (in-progress)"
    ] = None,
    time_hours: Annotated[int | None, "Filter by last N hours"] = None,
    limit: Annotated[int, "Maximum number of results"] = 10,
    ctx: Context | None = None,
) -> SearchResponse:
    """Search deployment logs using LlamaIndex semantic search.

    This tool uses a production-grade RAG pipeline:
    1. Query is embedded with Mistral AI (1024 dimensions)
    2. Semantic search in Qdrant vector store
    3. Metadata filtering (sandbox, event type, time, etc.)
    4. Results ranked by relevance with source citations

    Args:
        query: Natural language search query
        sandbox_name: Optional sandbox name filter
        event_type: Optional event type filter
        return_code: Optional return code filter
        time_hours: Optional time range filter
        limit: Maximum results to return
        ctx: MCP context

    Returns:
        Search results with metadata and source citations
    """
    index = get_fleet_index()

    # Perform search with LlamaIndex
    results = index.search(
        query=query,
        sandbox_name=sandbox_name,
        event_type=event_type,
        return_code=return_code,
        time_hours=time_hours,
        limit=limit,
    )

    # Build filters applied summary
    filters_applied = {}
    if sandbox_name:
        filters_applied["sandbox_name"] = sandbox_name
    if event_type:
        filters_applied["event_type"] = event_type
    if return_code is not None:
        filters_applied["return_code"] = return_code
    if time_hours:
        filters_applied["time_hours"] = time_hours

    return {
        "query": query,
        "total_found": len(results),
        "results": results,
        "filters_applied": filters_applied,
    }


@mcp.tool(
    name="fleet_suggest_fix",
    description=(
        "[FIX] **AI-Powered Fix Suggestions** from successful deployments.\n\n"
        "Uses LlamaIndex RAG to find similar successful deployments:\n"
        "- Semantic similarity matching with Mistral embeddings\n"
        "- Only suggests from successful deployments (return_code=0)\n"
        "- Automatic deduplication by repository\n"
        "- Relevance-ranked suggestions\n\n"
        "**How It Works:**\n"
        "1. Embeds your problem description with Mistral AI\n"
        "2. Searches successful deployments in Qdrant\n"
        "3. Ranks by semantic similarity\n"
        "4. Returns deployments that solved similar problems\n\n"
        "**Parameters:**\n"
        "- context (str, required): Problem description\n"
        "- sandbox_name (str, optional): Bias to specific sandbox\n"
        "- limit (int, optional): Max suggestions (default: 5)\n\n"
        "**Returns:**\n"
        "- Successful deployments that solved similar problems\n"
        "- Repository URLs, deploy times, preview URLs\n"
        "- Relevance scores and timestamps\n"
        "- 100% success rate (only successful deployments)\n\n"
        "**Examples:**\n"
        "- 'npm build failed with module not found'\n"
        "- 'nginx not starting on port 3000'\n"
        "- 'git clone authentication failed'\n"
        "- 'deployment timeout after 5 minutes'"
    ),
)
@weave.op()
def fleet_suggest_fix(
    context: Annotated[str, "Problem description or error message"],
    sandbox_name: Annotated[
        str | None, "Optional sandbox name for context-specific suggestions"
    ] = None,
    limit: Annotated[int, "Maximum number of suggestions"] = 5,
    ctx: Context | None = None,
) -> SuggestResponse:
    """Suggest fixes from successful deployments using LlamaIndex.

    This tool uses semantic search to find successful deployments
    that solved similar problems:
    1. Embeds problem description with Mistral AI
    2. Searches only successful deployments (return_code=0)
    3. Ranks by semantic similarity
    4. Deduplicates by repository URL

    Args:
        context: Problem description or error message
        sandbox_name: Optional sandbox for context
        limit: Maximum suggestions to return
        ctx: MCP context

    Returns:
        Fix suggestions from successful deployments
    """
    index = get_fleet_index()

    # Get suggestions from LlamaIndex
    suggestions = index.suggest_fixes(
        problem_description=context,
        sandbox_name=sandbox_name,
        limit=limit,
    )

    return {
        "context": context,
        "sandbox_name": sandbox_name,
        "total_suggestions": len(suggestions),
        "suggestions": suggestions,
    }
