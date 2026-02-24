#!/usr/bin/env python3
"""
Test Elasticsearch connection for Elastic Infra Commander
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from elasticsearch import Elasticsearch
except ImportError:
    print("Installing elasticsearch package...")
    import sys
    os.system(f"{sys.executable} -m pip install elasticsearch")
    from elasticsearch import Elasticsearch

def test_connection():
    """Test Elasticsearch connection"""
    print("=" * 60)
    print("Elasticsearch Connection Test")
    print("=" * 60)
    
    # Get credentials from environment
    es_url = os.getenv("ELASTICSEARCH_URL")
    es_api_key = os.getenv("ELASTICSEARCH_API_KEY")
    
    if not es_url or not es_api_key:
        print("❌ Missing credentials!")
        print("   Set ELASTICSEARCH_URL and ELASTICSEARCH_API_KEY in .env")
        return False
    
    print(f"\nConnecting to: {es_url}")
    
    try:
        # Create Elasticsearch client
        es = Elasticsearch(
            es_url,
            api_key=es_api_key,
            request_timeout=30
        )
        
        # Test connection
        info = es.info()
        
        print(f"✅ Connected successfully!")
        print(f"\nCluster Info:")
        print(f"  Name: {info.get('cluster_name', 'N/A')}")
        print(f"  Version: {info.get('version', {}).get('number', 'N/A')}")
        print(f"  Tagline: {info.get('tagline', 'N/A')}")
        
        # List available indices
        print(f"\n📊 Available Indices:")
        indices = es.cat.indices(format='json', h='index,docs.count,store.size')
        
        if indices:
            for idx in indices[:10]:  # Show first 10
                print(f"  - {idx['index']}: {idx.get('docs.count', '0')} docs, {idx.get('store.size', '0')}")
            if len(indices) > 10:
                print(f"  ... and {len(indices) - 10} more indices")
        else:
            print("  No indices found (cluster is empty)")
        
        print("\n" + "=" * 60)
        print("✅ Elasticsearch connection test PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify ELASTICSEARCH_URL is correct")
        print("  2. Verify ELASTICSEARCH_API_KEY is valid")
        print("  3. Check if cluster is running")
        print("  4. Ensure API key has proper permissions")
        return False

if __name__ == "__main__":
    test_connection()
