#!/usr/bin/env python3
"""
Test runner connections to Elasticsearch and Blaxel
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_connections():
    print("=" * 60)
    print("Testing Runner Connections")
    print("=" * 60)
    
    # Test Elasticsearch
    print("\n1. Testing Elasticsearch...")
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(
            os.getenv("ELASTICSEARCH_URL"),
            api_key=os.getenv("ELASTICSEARCH_API_KEY"),
            request_timeout=30
        )
        info = es.info()
        print(f"   ✅ Elasticsearch connected")
        print(f"      Cluster: {info.get('cluster_name')}")
        print(f"      Version: {info.get('version', {}).get('number')}")
        
        # Check indices
        indices = ["distributed-tool-requests", "distributed-tool-results", 
                   "deployment-logs", "sandbox-latency"]
        for idx in indices:
            try:
                count = es.count(index=idx)["count"]
                print(f"      Index '{idx}': {count} docs")
            except:
                print(f"      Index '{idx}': not found (will be created)")
        
    except Exception as e:
        print(f"   ❌ Elasticsearch failed: {e}")
        return False
    
    # Test Blaxel
    print("\n2. Testing Blaxel...")
    try:
        from blaxel.core import SandboxInstance
        
        api_key = os.getenv("BL_API_KEY")
        workspace = os.getenv("BL_WORKSPACE")
        
        sandboxes = await SandboxInstance.list()
        
        print(f"   ✅ Blaxel connected")
        print(f"      Workspace: {workspace}")
        print(f"      Available VMs: {len(sandboxes)}")
        
        for i, sb in enumerate(sandboxes[:3], 1):
            print(f"      VM {i}: {sb.name}")
        
        if len(sandboxes) > 3:
            print(f"      ... and {len(sandboxes) - 3} more")
        
    except Exception as e:
        print(f"   ❌ Blaxel failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All connections successful!")
    print("=" * 60)
    print("\nRunner is ready to start:")
    print("  py runner/distributed_runner.py")
    return True

if __name__ == "__main__":
    asyncio.run(test_connections())
