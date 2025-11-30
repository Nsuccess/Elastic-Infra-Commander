"""
Test deployment using the OFFICIAL Blaxel pattern from their NextJS example.
This should work if we follow their pattern exactly.
"""
import asyncio
import os
from datetime import datetime, timedelta, timezone

# Load environment variables BEFORE importing Blaxel
from dotenv import load_dotenv
load_dotenv()

os.environ['BL_WORKSPACE'] = os.getenv('BL_WORKSPACE', '')
os.environ['BL_API_KEY'] = os.getenv('BL_API_KEY', '')

from blaxel.core import SandboxInstance

async def test_official_pattern():
    print("=" * 80)
    print("TESTING OFFICIAL BLAXEL PATTERN (from NextJS example)")
    print("=" * 80)
    
    # Step 1: Create sandbox
    print("\n1️⃣ Creating sandbox...")
    sandbox = await SandboxInstance.create({
        "metadata": {"name": f"test-official-{os.urandom(4).hex()}"},
        "spec": {
            "runtime": {
                "image": "blaxel/node:latest",
                "memory": 4096,
                "ports": [
                    {
                        "name": "preview",
                        "target": 3000,
                        "protocol": "HTTP"
                    }
                ]
            }
        }
    })
    
    sandbox_name = sandbox.metadata.name
    print(f"✅ Created: {sandbox_name}")
    
    # Wait for sandbox to be ready
    print("\n2️⃣ Waiting for sandbox to be ready...")
    await sandbox.wait()
    print("✅ Sandbox ready")
    
    # Step 2: Deploy the game
    print("\n3️⃣ Cloning repo...")
    await sandbox.process.exec({
        "command": "git clone https://github.com/Nsuccess/mcp-leap.git /app",
        "wait_for_completion": True
    })
    print("✅ Cloned")
    
    print("\n4️⃣ Installing dependencies...")
    await sandbox.process.exec({
        "name": "npm-ci",
        "command": "cd /app && npm ci",
        "wait_for_completion": False
    })
    await sandbox.process.wait("npm-ci", max_wait=180000)
    print("✅ Installed")
    
    print("\n5️⃣ Building...")
    await sandbox.process.exec({
        "name": "npm-build",
        "command": "cd /app && npm run build",
        "wait_for_completion": False
    })
    await sandbox.process.wait("npm-build", max_wait=60000)
    print("✅ Built")
    
    # Step 3: Start server on port 3000 (like NextJS example)
    print("\n6️⃣ Starting server on port 3000...")
    await sandbox.process.exec({
        "name": "serve-app",
        "command": "cd /app && npx serve -s dist -l 3000",
        "wait_for_completion": False
    })
    print("✅ Server started")
    
    # Wait for server to be ready
    await asyncio.sleep(5)
    
    # Verify server is running
    print("\n7️⃣ Verifying server is running...")
    result = await sandbox.process.exec({
        "command": "wget -q -O- http://127.0.0.1:3000 | head -c 100",
        "wait_for_completion": True
    })
    print(f"✅ Server responding: {result.logs[:100]}...")
    
    # Step 4: Create preview with TOKEN (official pattern)
    print("\n8️⃣ Creating preview with TOKEN authentication...")
    
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, X-Blaxel-Workspace, X-Blaxel-Preview-Token, X-Blaxel-Authorization",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Expose-Headers": "Content-Length, X-Request-Id",
        "Access-Control-Max-Age": "86400",
        "Vary": "Origin"
    }
    
    # Create preview (public: false, use token!)
    preview = await sandbox.previews.create_if_not_exists({
        "metadata": {"name": "preview"},
        "spec": {
            "port": 3000,
            "public": False,  # ← OFFICIAL PATTERN: Use token, not public
            "protocol": "HTTP",
            "responseHeaders": response_headers
        }
    })
    
    print(f"✅ Preview created: {preview.spec.url}")
    
    # Step 5: Create token (official pattern)
    print("\n9️⃣ Creating preview token...")
    token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)
    token = await preview.tokens.create(token_expiry)
    
    print(f"✅ Token created: {token.value[:20]}...")
    
    # Step 6: Build URL with token (official pattern)
    preview_url = f"{preview.spec.url}?bl_preview_token={token.value}"
    
    print(f"\n🎯 FINAL URL WITH TOKEN:")
    print(f"   {preview_url}")
    
    # Step 7: Test the URL
    print("\n🔟 Testing preview URL...")
    print("   (Waiting 10 seconds for routing...)")
    await asyncio.sleep(10)
    
    import httpx
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            print(f"   Making request to: {preview_url[:80]}...")
            response = await client.get(preview_url)
            print(f"\n   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS! Preview URL is working!")
                print(f"   Content preview: {response.text[:200]}...")
                
                # Check if it's the actual game
                if "MCP Leap" in response.text or "<!DOCTYPE html>" in response.text:
                    print("\n   🎮 GAME IS LIVE!")
                else:
                    print("\n   ⚠️  Got HTML but might not be the game")
            else:
                print(f"   ❌ Got {response.status_code}")
                print(f"   Response: {response.text[:500]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Sandbox: {sandbox_name}")
    print(f"Preview URL (no token): {preview.spec.url}")
    print(f"Preview URL (with token): {preview_url}")
    print("=" * 80)
    
    # Keep sandbox for inspection
    print("\n💡 Sandbox kept for inspection. Delete manually if needed.")
    print(f"   blaxel sandbox delete {sandbox_name}")

if __name__ == "__main__":
    asyncio.run(test_official_pattern())
