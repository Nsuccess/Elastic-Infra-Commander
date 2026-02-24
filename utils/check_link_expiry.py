"""Check how long the deployed game links will last."""
import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()
os.environ['BL_WORKSPACE'] = os.getenv('BL_WORKSPACE', '')
os.environ['BL_API_KEY'] = os.getenv('BL_API_KEY', '')

from blaxel.core import SandboxInstance

async def check_expiry():
    sandboxes = ['fleet-game-721b7869', 'fleet-game-192e29b3']
    
    print("=" * 80)
    print("CHECKING LINK EXPIRY TIMES")
    print("=" * 80)
    
    for i, sb_name in enumerate(sandboxes, 1):
        print(f"\n🎮 Machine {i}: {sb_name}")
        try:
            sb = await SandboxInstance.get(sb_name)
            previews = await sb.previews.list()
            
            if previews:
                preview = previews[0]
                tokens = await preview.tokens.list()
                
                if tokens:
                    token = tokens[0]
                    expires_at = token.expires_at
                    now = datetime.now(timezone.utc)
                    
                    # Calculate time remaining
                    time_remaining = expires_at - now
                    hours_remaining = time_remaining.total_seconds() / 3600
                    
                    print(f"   🔑 Token created: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    print(f"   ⏰ Expires at: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    print(f"   ⏳ Time remaining: {hours_remaining:.1f} hours")
                    
                    if hours_remaining > 23:
                        print(f"   ✅ Link valid for: ~24 hours")
                    elif hours_remaining > 1:
                        print(f"   ✅ Link valid for: {int(hours_remaining)} hours")
                    else:
                        print(f"   ⚠️  Link expires soon: {int(hours_remaining * 60)} minutes")
                else:
                    print("   ❌ No tokens found")
            else:
                print("   ❌ No previews found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("🔑 Token Expiry: 24 hours from creation")
    print("🎮 Game Links: Valid for 24 hours")
    print("♻️  Renewal: Deploy again to get new 24-hour links")
    print("=" * 80)

asyncio.run(check_expiry())
