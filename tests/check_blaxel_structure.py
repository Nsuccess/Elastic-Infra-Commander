#!/usr/bin/env python3
"""Check blaxel package structure"""

try:
    import blaxel
    print("✅ blaxel package found")
    print(f"   Location: {blaxel.__file__}")
    print(f"\n📦 Available in blaxel package:")
    for item in dir(blaxel):
        if not item.startswith('_'):
            print(f"   - {item}")
    
    # Try to find the client class
    if hasattr(blaxel, 'Blaxel'):
        print("\n✅ Found: blaxel.Blaxel")
    if hasattr(blaxel, 'Client'):
        print("✅ Found: blaxel.Client")
    if hasattr(blaxel, 'BlaxelClient'):
        print("✅ Found: blaxel.BlaxelClient")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
