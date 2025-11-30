"""Get the full URLs from the deployed sandboxes"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['BL_WORKSPACE'] = os.getenv('BL_WORKSPACE', '')
os.environ['BL_API_KEY'] = os.getenv('BL_API_KEY', '')

from blaxel.core import SandboxInstance

async def test():
    sandboxes = ['fleet-game-4243cdcc', 'fleet-game-b2e2bae6', 'fleet-game-af416ce1']
    
    print("=" * 80)
    print("GETTING FULL PREVIEW URLS")
    print("=" * 80)
    
    for sb_name in sandboxes:
        print(f"\n{sb_name}:")
        try:
            sb = await SandboxInstance.get(sb_name)
            previews = await sb.previews.list()
            
            if previews:
                preview = previews[0]
                tokens = await preview.tokens.list()
                
                if tokens:
                    token = tokens[0]
                    full_url = f"{preview.spec.url}?bl_preview_token={token.value}"
                    print(f"  Full URL: {full_url}")
                    
                    # Test it
                    import httpx
                    async with httpx.AsyncClient(timeout=10) as client:
                        try:
                            resp = await client.get(full_url)
                            print(f"  Status: {resp.status_code}")
                            if resp.status_code == 200:
                                print(f"  ✅ WORKING!")
                            else:
                                print(f"  ❌ Error: {resp.status_code}")
                        except Exception as e:
                            print(f"  ❌ Error: {e}")
                else:
                    print("  No tokens found")
            else:
                print("  No previews found")
                
        except Exception as e:
            print(f"  Error: {e}")

asyncio.run(test())
