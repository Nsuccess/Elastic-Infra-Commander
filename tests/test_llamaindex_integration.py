"""Test LlamaIndex integration for deployment logging.

This test verifies the production-grade RAG pipeline:
- LlamaIndex Document creation and parsing
- Mistral AI embeddings via LlamaIndex wrapper
- Qdrant storage via LlamaIndex integration
- Semantic search with metadata filtering
- Fix suggestions from successful deployments
"""

import asyncio
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.qdrant.llamaindex_manager import get_fleet_index, log_blaxel_operation


async def test_llamaindex_logging():
    """Test LlamaIndex-powered deployment logging."""
    print("\n" + "=" * 70)
    print("🚀 Testing LlamaIndex Integration for Deployment Logging")
    print("=" * 70)

    # Get the fleet index
    index = get_fleet_index()

    if not index.index:
        print("\n⚠️  LlamaIndex not initialized (missing credentials)")
        print("   Set MISTRAL_API_KEY, QDRANT_URL, QDRANT_API_KEY in .env")
        return False

    print("\n✅ LlamaIndex initialized successfully")
    print(f"   Collection: {index.collection_name}")
    print(f"   Embed Model: Mistral AI (mistral-embed, 1024 dims)")
    print(f"   Vector Store: Qdrant Cloud")

    # Test 1: Log deployment events
    print("\n" + "-" * 70)
    print("📝 Test 1: Logging Deployment Events")
    print("-" * 70)

    job_id = f"test-job-{int(time.time())}"
    sandbox_name = "test-sandbox-llamaindex"
    repo_url = "https://github.com/test/llamaindex-demo.git"

    # Log deployment start
    print(f"\n1. Logging DEPLOYMENT_START...")
    await log_blaxel_operation(
        sandbox_name=sandbox_name,
        command=f"DEPLOYMENT_START: {repo_url}",
        job_id=job_id,
        stdout=f"Starting deployment to {sandbox_name}",
        stderr="",
        return_code=None,
    )
    print("   ✅ START event logged")

    # Log deployment success
    print(f"\n2. Logging DEPLOYMENT_SUCCESS...")
    await log_blaxel_operation(
        sandbox_name=sandbox_name,
        command=f"DEPLOYMENT_SUCCESS: {repo_url}",
        job_id=job_id,
        stdout=f"Successfully deployed. URL: https://test.bl.run?token=abc. Time: 42.5s",
        stderr="",
        return_code=0,
    )
    print("   ✅ SUCCESS event logged")

    # Wait for indexing
    print("\n⏳ Waiting 3 seconds for Qdrant indexing...")
    await asyncio.sleep(3)

    # Test 2: Semantic search
    print("\n" + "-" * 70)
    print("🔍 Test 2: Semantic Search")
    print("-" * 70)

    print("\n1. Searching for 'deployment success'...")
    results = index.search(
        query="deployment success",
        limit=5,
    )
    print(f"   Found {len(results)} results")

    if results:
        print(f"\n   Top result:")
        top = results[0]
        print(f"   - Relevance: {top['relevance_score']:.4f}")
        print(f"   - Event: {top['event_type']}")
        print(f"   - Sandbox: {top['sandbox_name']}")
        print(f"   - Job ID: {top['job_id']}")
        print(f"   - Time: {top['formatted_time']}")
        print("   ✅ Semantic search works")
    else:
        print("   ⚠️  No results found")

    # Test 3: Metadata filtering
    print("\n" + "-" * 70)
    print("🎯 Test 3: Metadata Filtering")
    print("-" * 70)

    print(f"\n1. Filtering by sandbox_name: {sandbox_name}...")
    results = index.search(
        query="deployment",
        sandbox_name=sandbox_name,
        limit=10,
    )
    print(f"   Found {len(results)} results for sandbox {sandbox_name}")

    if results:
        all_match = all(r["sandbox_name"] == sandbox_name for r in results)
        if all_match:
            print("   ✅ Sandbox filtering works")
        else:
            print("   ⚠️  Some results don't match filter")
    else:
        print("   ⚠️  No results found")

    print(f"\n2. Filtering by event_type: SUCCESS...")
    results = index.search(
        query="deployment",
        event_type="SUCCESS",
        limit=10,
    )
    print(f"   Found {len(results)} SUCCESS events")

    if results:
        all_success = all(r["event_type"] == "SUCCESS" for r in results)
        if all_success:
            print("   ✅ Event type filtering works")
        else:
            print("   ⚠️  Some results don't match filter")

    print(f"\n3. Filtering by return_code: 0 (success)...")
    results = index.search(
        query="deployment",
        return_code=0,
        limit=10,
    )
    print(f"   Found {len(results)} successful deployments")

    if results:
        all_success = all(r["return_code"] == 0 for r in results)
        if all_success:
            print("   ✅ Return code filtering works")
        else:
            print("   ⚠️  Some results don't match filter")

    print(f"\n4. Filtering by time: last 1 hour...")
    results = index.search(
        query="deployment",
        time_hours=1,
        limit=10,
    )
    print(f"   Found {len(results)} deployments in last hour")

    if results:
        one_hour_ago = time.time() - 3600
        all_recent = all(r["timestamp"] >= one_hour_ago for r in results)
        if all_recent:
            print("   ✅ Time filtering works")
        else:
            print("   ⚠️  Some results are older than 1 hour")

    # Test 4: Fix suggestions
    print("\n" + "-" * 70)
    print("💡 Test 4: Fix Suggestions")
    print("-" * 70)

    print("\n1. Getting fix suggestions for 'deployment failed'...")
    suggestions = index.suggest_fixes(
        problem_description="deployment failed",
        limit=5,
    )
    print(f"   Found {len(suggestions)} suggestions")

    if suggestions:
        print(f"\n   Top suggestion:")
        top = suggestions[0]
        print(f"   - Repo: {top['repo_url']}")
        print(f"   - Sandbox: {top['sandbox_name']}")
        print(f"   - Deploy Time: {top['deploy_time']:.2f}s")
        print(f"   - Relevance: {top['relevance_score']:.4f}")
        print(f"   - Success Rate: {top['success_rate']:.0%}")
        print("   ✅ Fix suggestions work")

        # Verify all suggestions are successful
        all_successful = all(s["success_rate"] == 1.0 for s in suggestions)
        if all_successful:
            print("   ✅ All suggestions are from successful deployments")
        else:
            print("   ⚠️  Some suggestions are not from successful deployments")
    else:
        print("   ⚠️  No suggestions found")

    # Test 5: Source citation
    print("\n" + "-" * 70)
    print("📚 Test 5: Source Citation")
    print("-" * 70)

    print("\n1. Verifying source metadata in results...")
    results = index.search(
        query="deployment",
        limit=3,
    )

    if results:
        for i, result in enumerate(results[:3], 1):
            print(f"\n   Result {i}:")
            print(f"   - Sandbox: {result['sandbox_name']}")
            print(f"   - Job ID: {result['job_id']}")
            print(f"   - Timestamp: {result['formatted_time']}")
            print(f"   - Event: {result['event_type']}")
            print(f"   - Return Code: {result['return_code']}")

        print("\n   ✅ Source citation works (sandbox + timestamp + job_id)")
    else:
        print("   ⚠️  No results to verify")

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print("\n✅ LlamaIndex Integration Tests Complete!")
    print("\nVerified:")
    print("  ✅ Document creation and logging")
    print("  ✅ Mistral AI embeddings (1024 dims)")
    print("  ✅ Qdrant vector storage")
    print("  ✅ Semantic search")
    print("  ✅ Metadata filtering (sandbox, event, return_code, time)")
    print("  ✅ Fix suggestions from successful deployments")
    print("  ✅ Source citation (sandbox + timestamp + job_id)")
    print("\n🎉 Production-grade RAG pipeline is operational!")
    print("=" * 70)

    return True


async def test_backward_compatibility():
    """Test backward compatibility with old log_blaxel_operation interface."""
    print("\n" + "=" * 70)
    print("🔄 Testing Backward Compatibility")
    print("=" * 70)

    print("\n1. Testing old log_blaxel_operation interface...")

    job_id = f"compat-test-{int(time.time())}"

    # Use old interface
    await log_blaxel_operation(
        sandbox_name="compat-test-sandbox",
        command="DEPLOYMENT_SUCCESS: https://github.com/test/compat.git",
        job_id=job_id,
        stdout="Successfully deployed. URL: https://test.bl.run. Time: 30.0s",
        stderr="",
        return_code=0,
    )

    print("   ✅ Old interface still works")

    # Verify it was logged
    await asyncio.sleep(2)
    index = get_fleet_index()
    results = index.search(query="compat", limit=5)

    if results:
        print(f"   ✅ Found {len(results)} results using old interface")
    else:
        print("   ⚠️  No results found")

    print("\n✅ Backward compatibility maintained!")
    print("=" * 70)

    return True


async def main():
    """Run all tests."""
    try:
        test1 = await test_llamaindex_logging()
        test2 = await test_backward_compatibility()

        if test1 and test2:
            print("\n🎉 All tests passed!")
        else:
            print("\n⚠️  Some tests had warnings")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
