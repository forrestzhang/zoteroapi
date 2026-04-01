#!/usr/bin/env python3
"""
Query paper information by PMID from Zotero local library.

This script searches Zotero for papers by their PMID and outputs
detailed information in various formats.

Usage:
    # Query single PMID
    python scripts/query_by_pmid.py 39122952

    # Query multiple PMIDs
    python scripts/query_by_pmid.py 39122952 40931188 6305503

    # Query from file
    python scripts/query_by_pmid.py --file pmids.txt

    # Specify output format
    python scripts/query_by_pmid.py 39122952 --format json
    python scripts/query_by_pmid.py 39122952 --format markdown

    # Save to file
    python scripts/query_by_pmid.py 39122952 --output results.json
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

try:
    from zoteroapi import ZoteroLocal
except ImportError:
    print("Error: zoteroapi not installed. Please run:")
    print("  pip install zoteroapi")
    sys.exit(1)


def extract_pmid(item: Dict) -> str | None:
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


def format_authors(creators: List[Dict]) -> str:
    """Format authors list."""
    if not creators:
        return "N/A"

    authors = []
    for creator in creators:
        # Try to get name from firstName + lastName
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

    if not authors:
        return "N/A"

    if len(authors) <= 3:
        return ", ".join(authors)
    else:
        return ", ".join(authors[:3]) + " et al."


def has_attachment(item: Dict) -> str:
    """Check if item has attachment."""
    links = item.get('links', {})
    if 'attachment' in links:
        attachment_type = links['attachment'].get('attachmentType', 'unknown')
        return f"Yes ({attachment_type})"
    return "No"


def format_tags(tags: List[Dict]) -> str:
    """Format tags list."""
    if not tags:
        return "N/A"
    return ", ".join([tag.get('tag', '') for tag in tags[:5]])


def output_table(items: List[Dict], verbose: bool = False) -> None:
    """Output items in table format."""
    try:
        from tabulate import tabulate
    except ImportError:
        print("Error: tabulate not installed. Install with:")
        print("  pip install tabulate")
        # Fallback to simple format
        output_simple_table(items, verbose)
        return

    headers = ["PMID", "Title", "Authors", "Journal", "Year", "DOI"]
    if verbose:
        headers.extend(["Abstract", "Tags", "Attachment"])

    rows = []
    for item in items:
        data = item['data']
        pmid = extract_pmid(item) or "N/A"
        title = data.get('title', 'N/A')
        # Truncate title for table
        if len(title) > 60:
            title = title[:57] + "..."
        authors = format_authors(data.get('creators', []))
        journal = data.get('publicationTitle', 'N/A')
        year = data.get('date', 'N/A')[:4] if data.get('date') else "N/A"
        doi = data.get('DOI', 'N/A')

        row = [pmid, title, authors, journal, year, doi]

        if verbose:
            abstract = data.get('abstractNote', 'N/A')
            if len(abstract) > 100:
                abstract = abstract[:97] + "..."
            tags = format_tags(data.get('tags', []))
            attachment = has_attachment(item)
            row.extend([abstract, tags, attachment])

        rows.append(row)

    print(tabulate(rows, headers=headers, tablefmt="grid"))


def output_simple_table(items: List[Dict], verbose: bool = False) -> None:
    """Output items in simple table format (fallback)."""
    for item in items:
        data = item['data']
        pmid = extract_pmid(item) or "N/A"
        title = data.get('title', 'N/A')
        authors = format_authors(data.get('creators', []))
        journal = data.get('publicationTitle', 'N/A')
        year = data.get('date', 'N/A')[:4] if data.get('date') else "N/A"
        doi = data.get('DOI', 'N/A')

        print(f"\n{'='*80}")
        print(f"PMID:    {pmid}")
        print(f"Title:   {title}")
        print(f"Authors: {authors}")
        print(f"Journal: {journal}")
        print(f"Year:    {year}")
        print(f"DOI:     {doi}")

        if verbose:
            print(f"Abstract: {data.get('abstractNote', 'N/A')}")
            print(f"Tags: {format_tags(data.get('tags', []))}")
            print(f"Attachment: {has_attachment(item)}")


def output_json(items: List[Dict], output_file: str = None) -> None:
    """Output items in JSON format."""
    result = []
    for item in items:
        data = item['data']

        # Extract authors with proper name formatting
        authors = []
        for creator in data.get('creators', []):
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

        result.append({
            'pmid': extract_pmid(item),
            'key': item['key'],
            'title': data.get('title'),
            'authors': authors,
            'abstract': data.get('abstractNote'),
            'journal': data.get('publicationTitle'),
            'volume': data.get('volume'),
            'issue': data.get('issue'),
            'pages': data.get('pages'),
            'date': data.get('date'),
            'doi': data.get('DOI'),
            'tags': [t.get('tag') for t in data.get('tags', [])],
            'has_attachment': 'attachment' in item.get('links', {}),
            'item_type': data.get('itemType')
        })

    json_str = json.dumps(result, indent=2, ensure_ascii=False)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"Results saved to {output_file}")
    else:
        print(json_str)


def output_markdown(items: List[Dict], verbose: bool = False) -> None:
    """Output items in Markdown format."""
    for i, item in enumerate(items, 1):
        data = item['data']
        pmid = extract_pmid(item) or "N/A"
        title = data.get('title', 'N/A')
        authors = format_authors(data.get('creators', []))
        journal = data.get('publicationTitle', 'N/A')
        year = data.get('date', 'N/A')[:4] if data.get('date') else "N/A"
        doi = data.get('DOI', 'N/A')
        volume = data.get('volume', '')
        issue = data.get('issue', '')
        pages = data.get('pages', '')

        print(f"\n## {i}. {title}")
        print()
        print(f"**PMID**: {pmid}  ")
        print(f"**Authors**: {authors}  ")
        print(f"**Journal**: {journal}", end='')
        if volume:
            print(f", **Volume**: {volume}", end='')
        if issue:
            print(f", **Issue**: {issue}", end='')
        if pages:
            print(f", **Pages**: {pages}", end='')
        print(f" ({year})")
        print(f"**DOI**: [{doi}](https://doi.org/{doi})  " if doi != "N/A" else "**DOI**: N/A  ")

        if verbose:
            abstract = data.get('abstractNote', '')
            if abstract:
                print(f"\n**Abstract**:\n\n{abstract}")

            tags = data.get('tags', [])
            if tags:
                tag_list = ", ".join([t.get('tag') for t in tags])
                print(f"\n**Tags**: {tag_list}")

            attachment = has_attachment(item)
            print(f"\n**Attachment**: {attachment}")


def query_pmids(pmids: List[str], format_type: str = 'table',
                 verbose: bool = False, output_file: str = None) -> None:
    """Query papers by PMID and output information."""
    client = ZoteroLocal()

    results = {
        'found': [],
        'not_found': []
    }

    for pmid in pmids:
        items = client.search_by_pmid(pmid)
        if items:
            results['found'].extend(items)
        else:
            results['not_found'].append(pmid)

    # Output results based on format
    if format_type == 'json':
        output_json(results['found'], output_file)
    elif format_type == 'markdown':
        output_markdown(results['found'], verbose)
    else:  # table
        output_table(results['found'], verbose)

    # Show not found PMIDs
    if results['not_found']:
        print(f"\n⚠️  PMIDs not found in library: {', '.join(results['not_found'])}")

    # Summary
    print(f"\n{'='*60}")
    print(f"Found: {len(results['found'])} papers")
    if results['not_found']:
        print(f"Not found: {len(results['not_found'])} PMIDs")
    print(f"Total queried: {len(pmids)}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Query paper information by PMID from Zotero local library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query single PMID
  %(prog)s 39122952

  # Query multiple PMIDs
  %(prog)s 39122952 40931188 6305503

  # Query from file
  %(prog)s --file pmids.txt

  # Output as JSON
  %(prog)s 39122952 --format json

  # Output as Markdown
  %(prog)s 39122952 --format markdown

  # Include abstract and tags
  %(prog)s 39122952 --verbose

  # Save to file
  %(prog)s 39122952 --format json --output results.json
        """
    )

    parser.add_argument(
        'pmids',
        nargs='*',
        help='PMIDs to query (can be multiple)'
    )

    parser.add_argument(
        '--file', '-f',
        help='Read PMIDs from file (one per line)'
    )

    parser.add_argument(
        '--format', '-F',
        choices=['table', 'json', 'markdown'],
        default='table',
        help='Output format (default: table)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Include abstract, tags, and attachment info'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file (only for JSON format)'
    )

    args = parser.parse_args()

    # Get PMIDs from arguments or file
    pmids = list(args.pmids) if args.pmids else []

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)

        with open(file_path, 'r') as f:
            file_pmids = [line.strip() for line in f if line.strip()]
            pmids.extend(file_pmids)

    if not pmids:
        parser.print_help()
        sys.exit(1)

    # Query PMIDs
    try:
        query_pmids(pmids, args.format, args.verbose, args.output)
    except KeyboardInterrupt:
        print("\n\nQuery cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
