#!/usr/bin/env python3
"""
Zotero Search Tool - Universal search interface for Zotero local library.

This script provides a unified interface to search Zotero by various methods
(PMID, DOI, keywords, title) and export results in structured JSON format.

Usage:
    # Search by PMID
    python scripts/zotero_search.py --pmid 12345678 --output results.json

    # Search by DOI
    python scripts/zotero_search.py --doi "10.1038/nature12373" --output results.json

    # Search by keywords
    python scripts/zotero_search.py --search "machine learning" --output results.json

    # Search by title
    python scripts/zotero_search.py --title "Deep Learning" --output results.json

    # Use as Python API
    from zotero_search import ZoteroSearch
    searcher = ZoteroSearch()
    results = searcher.search_by_keyword("machine learning")
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

try:
    from zoteroapi import ZoteroLocal
except ImportError:
    print("Error: zoteroapi not installed. Please run:")
    print("  pip install zoteroapi")
    sys.exit(1)


def extract_pmid(item: Dict) -> Optional[str]:
    """Extract PMID from item.

    Checks for dedicated PMID field (newer Zotero versions) first,
    then falls back to parsing from extra field (older versions).
    """
    # Check for dedicated PMID field (newer Zotero versions)
    pmid = item.get('data', {}).get('PMID')
    if pmid is not None and pmid.strip():
        return pmid.strip()

    # Fallback: parse from extra field (older Zotero versions)
    extra = item.get('data', {}).get('extra', '')
    for line in extra.split('\n'):
        if line.startswith('PMID:'):
            return line.split(':', 1)[1].strip()
    return None


def format_authors(creators: List[Dict]) -> List[str]:
    """Format authors list."""
    if not creators:
        return []

    authors = []
    for creator in creators:
        first = creator.get('firstName', '')
        last = creator.get('lastName', '')
        name = creator.get('name', '')

        if name:
            authors.append(name)
        elif first and last:
            authors.append(f"{first} {last}")
        elif last:
            authors.append(last)
        elif first:
            authors.append(first)

    return authors


def item_to_dict(item: Dict) -> Dict[str, Any]:
    """Convert Zotero item to standardized dictionary format."""
    data = item['data']

    # Extract authors with proper name formatting
    authors = format_authors(data.get('creators', []))

    return {
        'key': item['key'],
        'pmid': extract_pmid(item),
        'doi': data.get('DOI', ''),
        'title': data.get('title', ''),
        'authors': authors,
        'abstract': data.get('abstractNote', ''),
        'journal': data.get('publicationTitle', ''),
        'volume': data.get('volume', ''),
        'issue': data.get('issue', ''),
        'pages': data.get('pages', ''),
        'date': data.get('date', ''),
        'year': data.get('date', '')[:4] if data.get('date') else '',
        'tags': [t.get('tag') for t in data.get('tags', [])],
        'has_attachment': 'attachment' in item.get('links', {}),
        'item_type': data.get('itemType', ''),
        'url': data.get('url', '')
    }


class ZoteroSearch:
    """
    Unified search interface for Zotero local library.

    This class provides a Python API for searching Zotero and exporting
    results in a structured format suitable for other tools to use.
    """

    def __init__(self):
        """Initialize the Zotero search client."""
        self.client = ZoteroLocal()

    def search_by_pmid(self, pmid: str) -> List[Dict[str, Any]]:
        """
        Search Zotero library by PMID.

        Uses the underlying zoteroapi library which supports both
        dedicated PMID field (newer Zotero) and extra field (older Zotero).

        Args:
            pmid: PubMed ID

        Returns:
            List of paper dictionaries with standardized format
        """
        items = self.client.search_by_pmid(pmid)
        return [item_to_dict(item) for item in items]

    def search_by_doi(self, doi: str) -> List[Dict[str, Any]]:
        """
        Search Zotero library by DOI.

        Args:
            doi: Digital Object Identifier

        Returns:
            List of paper dictionaries with standardized format
        """
        items = self.client.search_by_doi(doi)
        return [item_to_dict(item) for item in items]

    def search_by_keyword(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search Zotero library by keywords.

        Args:
            query: Search query string
            limit: Maximum number of results to return (None for all)

        Returns:
            List of paper dictionaries with standardized format
        """
        items = self.client.search_items(query)
        if limit:
            items = items[:limit]
        return [item_to_dict(item) for item in items]

    def search_by_title(self, title: str, exact_match: bool = False) -> List[Dict[str, Any]]:
        """
        Search Zotero library by title.

        Args:
            title: Title to search for
            exact_match: Whether to use exact match (default: fuzzy)

        Returns:
            List of paper dictionaries with standardized format
        """
        items = self.client.search_by_title(title, exact_match=exact_match)
        return [item_to_dict(item) for item in items]

    def search(self, mode: str, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Generic search method.

        Args:
            mode: Search mode ('pmid', 'doi', 'keyword', 'title')
            query: Search query
            **kwargs: Additional search parameters

        Returns:
            List of paper dictionaries with standardized format
        """
        mode_handlers = {
            'pmid': self.search_by_pmid,
            'doi': self.search_by_doi,
            'keyword': self.search_by_keyword,
            'title': self.search_by_title
        }

        handler = mode_handlers.get(mode)
        if not handler:
            raise ValueError(f"Unknown search mode: {mode}. Use: pmid, doi, keyword, title")

        return handler(query, **kwargs)


def save_results(results: List[Dict], output_path: str | Path, pretty: bool = True) -> None:
    """
    Save search results to JSON file.

    Args:
        results: List of paper dictionaries
        output_path: Path to output file
        pretty: Whether to format JSON with indentation
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    indent = 2 if pretty else None
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=indent, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Search Zotero local library and export results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by PMID
  %(prog)s --pmid 12345678 --output results.json

  # Search by DOI
  %(prog)s --doi "10.1038/nature12373" --output results.json

  # Search by keywords
  %(prog)s --search "machine learning" --output results.json

  # Search by title
  %(prog)s --title "Deep Learning" --output results.json

  # Limit results
  %(prog)s --search "machine learning" --limit 10 --output results.json

  # Print to stdout (no output file)
  %(prog)s --search "machine learning" --pretty
        """
    )

    # Search options (mutually exclusive)
    search_group = parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument(
        '--pmid',
        help='Search by PMID'
    )
    search_group.add_argument(
        '--doi',
        help='Search by DOI'
    )
    search_group.add_argument(
        '--search', '-s',
        help='Search by keywords'
    )
    search_group.add_argument(
        '--title',
        help='Search by title'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file path (if not specified, prints to stdout)'
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of results (for keyword search)'
    )

    parser.add_argument(
        '--pretty', '-p',
        action='store_true',
        default=True,
        help='Pretty print JSON output (default: True)'
    )

    parser.add_argument(
        '--no-pretty',
        action='store_false',
        dest='pretty',
        help='Disable pretty printing (compact JSON)'
    )

    parser.add_argument(
        '--exact',
        action='store_true',
        help='Use exact match for title search'
    )

    args = parser.parse_args()

    # Initialize searcher
    searcher = ZoteroSearch()

    # Perform search
    results = None
    mode = None
    query = None

    try:
        if args.pmid:
            mode, query = 'pmid', args.pmid
            results = searcher.search_by_pmid(args.pmid)
        elif args.doi:
            mode, query = 'doi', args.doi
            results = searcher.search_by_doi(args.doi)
        elif args.search:
            mode, query = 'keyword', args.search
            results = searcher.search_by_keyword(args.search, limit=args.limit)
        elif args.title:
            mode, query = 'title', args.title
            results = searcher.search_by_title(args.title, exact_match=args.exact)

        if not results:
            print(f"No results found for {mode}: {query}", file=sys.stderr)
            sys.exit(0)

        # Output results
        if args.output:
            save_results(results, args.output, pretty=args.pretty)
            print(f"Found {len(results)} result(s), saved to {args.output}", file=sys.stderr)
        else:
            indent = 2 if args.pretty else None
            json.dump(results, sys.stdout, indent=indent, ensure_ascii=False)

    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
