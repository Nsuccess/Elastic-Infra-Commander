#!/usr/bin/env python3
"""Check blaxel.core structure"""

try:
    from blaxel import core
    print("✅ blaxel.core imported")
    print(f"\n📦 Available in blaxel.core:")
    for item in dir(core):
        if not item.startswith('_'):
            print(f"   - {item}")
    
    # Check for client classes
    if hasattr(core, 'Blaxel'):
        print("\n✅ Found: blaxel.core.Blaxel")
    if hasattr(core, 'Client'):
        print("✅ Found: blaxel.core.Client")
    if hasattr(core, 'BlaxelClient'):
        print("✅ Found: blaxel.core.BlaxelClient")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
