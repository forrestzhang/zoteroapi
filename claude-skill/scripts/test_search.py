#!/usr/bin/env python3
"""
Test search functionality in Zotero library.

This script tests various search methods:
- PMID search
- DOI search
- Title search
- Keyword search

Usage:
    python scripts/test_search.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

try:
    from zoteroapi import ZoteroLocal

    print("Testing Zotero search functionality...")
    print("-" * 50)

    client = ZoteroLocal()

    # Test 1: Get some items to work with
    print("\n1. Getting sample items...")
    items = client.get_items_top(limit=10)
    print(f"   Found {len(items)} top-level items")

    if not items:
        print("   No items found. Add some items to Zotero first.")
        sys.exit(1)

    # Test 2: Check for PMID in items
    print("\n2. Checking for PMID in items...")
    pmid_items = []
    for item in items:
        extra = item.get('data', {}).get('extra', '')
        if 'PMID:' in extra:
            pmid_items.append(item)
            pmid = [line for line in extra.split('\n') if line.startswith('PMID:')][0].split(':')[1].strip()
            print(f"   Found PMID: {pmid} in '{item['data']['title']}'")
            break

    if not pmid_items:
        print("   No items with PMID found")
        print("   Tip: Add PMID to item's 'Extra' field as 'PMID: 12345678'")
    else:
        # Test PMID search
        print("\n3. Testing PMID search...")
        pmid = [line for line in pmid_items[0]['data']['extra'].split('\n') if line.startswith('PMID:')][0].split(':')[1].strip()
        results = client.search_by_pmid(pmid)
        if results:
            print(f"   ✓ PMID search found: {results[0]['data']['title']}")
        else:
            print(f"   ✗ PMID search failed for PMID: {pmid}")

    # Test 3: Check for DOI in items
    print("\n4. Checking for DOI in items...")
    doi_items = [item for item in items if item.get('data', {}).get('DOI')]

    if doi_items:
        doi = doi_items[0]['data']['DOI']
        print(f"   Found DOI: {doi} in '{doi_items[0]['data']['title']}'")

        # Test DOI search
        print("\n5. Testing DOI search...")
        results = client.search_by_doi(doi)
        if results:
            print(f"   ✓ DOI search found: {results[0]['data']['title']}")
        else:
            print(f"   ✗ DOI search failed for DOI: {doi}")
    else:
        print("   No items with DOI found")

    # Test 4: Title search
    print("\n6. Testing title search...")
    if items:
        title = items[0]['data']['title']
        # Use first few words for fuzzy search
        search_title = ' '.join(title.split()[:3])
        results = client.search_by_title(search_title, exact_match=False)
        print(f"   Searching for: '{search_title}'")
        if results:
            print(f"   ✓ Title search found {len(results)} results")
            print(f"     First result: {results[0]['data']['title']}")
        else:
            print(f"   ✗ Title search failed for: '{search_title}'")

    # Test 5: Keyword search
    print("\n7. Testing keyword search...")
    # Use first word of first title as keyword
    if items:
        keyword = items[0]['data']['title'].split()[0]
        results = client.search_items(keyword)
        print(f"   Searching for keyword: '{keyword}'")
        print(f"   ✓ Keyword search found {len(results)} results")

    print("\n" + "=" * 50)
    print("Search tests completed!")
    print("=" * 50)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
