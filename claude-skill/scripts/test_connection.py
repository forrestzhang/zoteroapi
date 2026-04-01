#!/usr/bin/env python3
"""
Test Zotero local server connection.

This script verifies that:
1. Zotero desktop app is running
2. Local server is enabled on port 23119
3. Can connect and retrieve data

Usage:
    python scripts/test_connection.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

try:
    from zoteroapi import ZoteroLocal, ZoteroLocalError

    print("Testing Zotero local server connection...")
    print("-" * 50)

    try:
        # Create client and test connection
        client = ZoteroLocal()

        # Try to get one item
        items = client.get_items_top(limit=1)

        print("✓ Connection successful!")
        print(f"✓ Found {len(items)} top-level items")

        if items:
            item = items[0]
            print(f"✓ Sample item: {item['data']['title']}")

        # Test getting collections
        collections = client.get_collections()
        print(f"✓ Found {len(collections)} collections")

        print("\n" + "=" * 50)
        print("All tests passed! Your Zotero local server is working.")
        print("=" * 50)

    except ZoteroLocalError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Zotero desktop app is running")
        print("2. Enable local server:")
        print("   - Edit > Preferences > Advanced > Config Editor")
        print("   - Search for: extensions.zotero.httpServer.enabled")
        print("   - Set value to: true")
        print("3. Restart Zotero")
        sys.exit(1)

except ImportError as e:
    print(f"\n✗ Import failed: {e}")
    print("\nPlease install zoteroapi:")
    print("  pip install zoteroapi")
    print("\nOr install in development mode:")
    print("  cd /path/to/zoteroapi")
    print("  pip install -e .")
    sys.exit(1)
