#!/usr/bin/env python3
"""
Distributed Runner - Polls Elasticsearch for deployment requests and executes them on Blaxel VMs
"""
import asyncio
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Set environment variables for Blaxel
os.environ['BL_WORKSPACE'] = os.getenv('BL_WORKSPACE', '')
os.environ['BL_API_KEY'] = os.getenv('BL_API_KEY', '')

from elasticsearch import Elasticsearch
from blaxel.core import SandboxInstance

# Elasticsearch client
es = Elasticsearch(
    os.getenv("ELASTICSEARCH_URL"),
    api_key=os.getenv("ELASTICSEARCH_API_KEY"),
    request_timeout=30
)

async def deploy_to_vm(repo_url: str, vm_number: int):
    """Deploy application to a single VM"""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Create sandbox
        print(f"  VM {vm_number}: Creating sandbox...")
        sandbox = await SandboxInstance.create({
            "metadata": {"name": f"elastic-deploy-{os.urandom(4).hex()}"},
            "spec": {
                "runtime": {
                    "image": "blaxel/node:latest",
                    "memory": 4096,
                    "ports": [{"name": "app", "target": 3000, "protocol": "HTTP"}]
                }
            }
        })
        
        sandbox_name = sandbox.metadata.name
        print(f"  VM {vm_number}: ✅ Sandbox created: {sandbox_name}")
        
        # Clone repository
        print(f"  VM {vm_number}: Cloning repository...")
        await sandbox.process.exec({
            "command": f"git clone {repo_url} /app",
            "wait_for_completion": True
        })
        
        # Install dependencies
        print(f"  VM {vm_number}: Installing dependencies...")
        await sandbox.process.exec({
            "command": "cd /app && npm ci",
            "wait_for_completion": True,
            "timeout": 180000
        })
        
        # Build application
        print(f"  VM {vm_number}: Building application...")
        await sandbox.process.exec({
            "command": "cd /app && npm run build",
            "wait_for_completion": True,
            "timeout": 60000
        })
        
        # Start server (non-blocking, runs in background)
        print(f"  VM {vm_number}: Starting server...")
        await sandbox.process.exec({
            "command": "cd /app && npx serve -s dist -l 3000",
            "wait_for_completion": False
        })
        
        # Wait for port 3000 to be ready
        await asyncio.sleep(5)
        
        # Create preview URL with token
        print(f"  VM {vm_number}: Creating preview URL...")
        from datetime import timedelta
        
        preview = await sandbox.previews.create_if_not_exists({
            "metadata": {"name": "preview"},
            "spec": {
                "port": 3000,
                "public": False,
                "protocol": "HTTP",
                "responseHeaders": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*"
                }
            }
        })
        
        token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)
        token = await preview.tokens.create(token_expiry)
        url = f"{preview.spec.url}?bl_preview_token={token.value}"
        
        deploy_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        print(f"  VM {vm_number}: ✅ DEPLOYED in {deploy_time:.1f}s")
        print(f"  VM {vm_number}: 🌐 {url}")
        
        return {
            "vm_number": vm_number,
            "sandbox_name": sandbox_name,
            "url": url,
            "deploy_time": deploy_time,
            "status": "success"
        }
        
    except Exception as e:
        deploy_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        print(f"  VM {vm_number}: ❌ FAILED: {e}")
        return {
            "vm_number": vm_number,
            "error": str(e),
            "deploy_time": deploy_time,
            "status": "failed"
        }

async def process_deployment_request(request):
    """Process a deployment request from Elasticsearch"""
    request_id = request['_id']
    source = request['_source']
    
    repo_url = source.get('repo_url')
    num_vms = int(source.get('num_vms', 2))  # Convert to int
    
    print(f"\n{'='*70}")
    print(f"📦 Processing Deployment Request: {request_id}")
    print(f"{'='*70}")
    print(f"Repository: {repo_url}")
    print(f"Target VMs: {num_vms}")
    print(f"")
    
    start_time = datetime.now(timezone.utc)
    
    # Update status to processing
    es.update(
        index="distributed-tool-requests",
        id=request_id,
        body={"doc": {"status": "processing", "started_at": start_time.isoformat()}}
    )
    
    # Deploy to VMs in parallel
    print(f"🚀 Deploying to {num_vms} VMs in parallel...")
    tasks = [deploy_to_vm(repo_url, i+1) for i in range(num_vms)]
    results = await asyncio.gather(*tasks)
    
    total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Store results
    result_doc = {
        "request_id": request_id,
        "repo_url": repo_url,
        "num_vms": num_vms,
        "deployments": results,
        "total_time": total_time,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed"
    }
    
    es.index(index="distributed-tool-results", document=result_doc)
    
    # Update request status
    es.update(
        index="distributed-tool-requests",
        id=request_id,
        body={"doc": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"✅ Deployment Complete!")
    print(f"{'='*70}")
    print(f"Total Time: {total_time:.1f}s")
    
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"Successful: {successful}/{num_vms}")
    
    print(f"\nLive URLs:")
    for result in results:
        if result['status'] == 'success':
            print(f"  • VM {result['vm_number']}: {result['url']}")
    print(f"{'='*70}\n")

async def poll_elasticsearch():
    """Poll Elasticsearch for new deployment requests"""
    print("=" * 70)
    print("🚀 Elastic Infra Commander - Distributed Runner")
    print("=" * 70)
    print(f"Elasticsearch: {os.getenv('ELASTICSEARCH_URL')}")
    print(f"Blaxel Workspace: {os.getenv('BL_WORKSPACE')}")
    print(f"\n⏳ Polling for deployment requests...")
    print(f"   (Press Ctrl+C to stop)\n")
    
    while True:
        try:
            # Query for pending requests
            response = es.search(
                index="distributed-tool-requests",
                body={
                    "query": {
                        "term": {"status": "pending"}
                    },
                    "size": 1,
                    "sort": [{"created_at": "asc"}]
                }
            )
            
            if response['hits']['total']['value'] > 0:
                request = response['hits']['hits'][0]
                await process_deployment_request(request)
            
            await asyncio.sleep(2)  # Poll every 2 seconds
            
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down runner...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(poll_elasticsearch())
    except KeyboardInterrupt:
        print("\n\n✅ Runner stopped")
        sys.exit(0)
