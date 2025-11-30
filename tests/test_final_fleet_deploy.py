"""Final test: Deploy to 3 sandboxes and verify all work"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['BL_WORKSPACE'] = os.getenv('BL_WORKSPACE', '')
os.environ['BL_API_KEY'] = os.getenv('BL_API_KEY', '')

from src.blaxel.tools import fleet_deploy_game

async def test():
    print("=" * 80)
    print("FINAL FLEET DEPLOYMENT TEST")
    print("=" * 80)
    print("\nDeploying MCP Leap game to 3 sandboxes...")
    print("This will test the complete working solution.\n")
    
    # Deploy to 3 sandboxes
    result = await fleet_deploy_game(
        repo_url="https://github.com/Nsuccess/mcp-leap.git",
        n=3
    )
    
    print("\n" + "=" * 80)
    print("DEPLOYMENT RESULTS")
    print("=" * 80)
    print(f"Total time: {result['total_time_seconds']}s")
    print(f"Repo: {result['repo_url']}")
    
    successful = 0
    failed = 0
    
    print(f"\nDeployments:")
    for i, deployment in enumerate(result['deployments'], 1):
        print(f"\n{i}. {deployment['sandbox_name']}")
        print(f"   Status: {deployment['status']}")
        print(f"   Time: {deployment['deploy_time_seconds']}s")
        
        if deployment['url']:
            print(f"   URL: {deployment['url'][:80]}...")
            
            # Test the URL
            import httpx
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.get(deployment['url'])
                    if resp.status_code == 200:
                        print(f"   ✅ LIVE! Game is accessible!")
                        if "MCP Leap" in resp.text or "<!DOCTYPE html>" in resp.text:
                            print(f"   🎮 Game content verified!")
                            successful += 1
                    else:
                        print(f"   ❌ Status: {resp.status_code}")
                        failed += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(successful/(successful+failed)*100):.1f}%")
    print("=" * 80)
    
    if successful == len(result['deployments']):
        print("\n🎉 ALL DEPLOYMENTS SUCCESSFUL!")
        print("The Blaxel Fleet Commander MCP Server is working perfectly!")
    elif successful > 0:
        print(f"\n⚠️  Partial success: {successful}/{len(result['deployments'])} working")
    else:
        print("\n❌ All deployments failed")

asyncio.run(test())
