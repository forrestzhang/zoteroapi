#!/usr/bin/env python3
"""
Batch export PDFs from Zotero collection.

This script allows exporting all PDFs from a specified collection
to a user-specified directory with customizable naming.

Usage:
    python scripts/batch_export.py "Collection Name" /path/to/output
    python scripts/batch_export.py "Collection Name" /path/to/output --naming title
    python scripts/batch_export.py "Collection Name" /path/to/output --naming doi

Arguments:
    collection_name: Name of the Zotero collection
    output_dir: Directory to save PDFs (will be created if not exists)

Naming Options:
    pmid     - Use PMID as filename (default): {pmid}.pdf
    title    - Use paper title: {title}.pdf
    doi      - Use DOI: {doi}.pdf
    combined - Combined: {pmid}_{title}.pdf or {title}.pdf if no PMID
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

try:
    from zoteroapi import ZoteroLocal, ZoteroLocalError

    def sanitize_filename(name: str) -> str:
        """Sanitize filename by removing invalid characters."""
        return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_', '.')).strip()

    def extract_pmid(item: dict) -> str | None:
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

    def get_filename(item: dict, naming_mode: str) -> str:
        """Generate filename based on naming mode."""
        title = item['data']['title']
        doi = item.get('data', {}).get('DOI', '')
        pmid = extract_pmid(item)

        if naming_mode == 'pmid':
            if pmid:
                return f"{pmid}.pdf"
            else:
                # Fallback to title if no PMID
                safe_title = sanitize_filename(title)
                return f"{safe_title}.pdf"

        elif naming_mode == 'doi':
            if doi:
                # Sanitize DOI for filename (replace / with _)
                safe_doi = doi.replace('/', '_')
                return f"{safe_doi}.pdf"
            else:
                safe_title = sanitize_filename(title)
                return f"{safe_title}.pdf"

        elif naming_mode == 'title':
            safe_title = sanitize_filename(title)
            return f"{safe_title}.pdf"

        elif naming_mode == 'combined':
            if pmid:
                safe_title = sanitize_filename(title)
                return f"{pmid}_{safe_title[:50]}.pdf"
            else:
                safe_title = sanitize_filename(title)
                return f"{safe_title}.pdf"

        else:
            # Default to PMID mode
            return get_filename(item, 'pmid')

    def batch_export(collection_name: str, output_dir: Path, naming_mode: str = 'pmid', verbose: bool = True):
        """Export all PDFs from a collection to the specified directory."""
        print(f"Batch Export from Zotero")
        print("=" * 50)
        print(f"Collection: {collection_name}")
        print(f"Output: {output_dir}")
        print(f"Naming: {naming_mode}")
        print("-" * 50)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize client
        client = ZoteroLocal()

        # Find collection
        collections = client.get_collections()
        target_collection = None

        for coll in collections:
            if coll['data']['name'] == collection_name:
                target_collection = coll
                break

        if not target_collection:
            print(f"\n✗ Collection '{collection_name}' not found")
            print("\nAvailable collections:")
            for coll in collections:
                print(f"  - {coll['data']['name']}")
            sys.exit(1)

        # Get items in collection
        items = client.get_collection_items(target_collection['key'])
        print(f"\nFound {len(items)} items in collection")

        # Filter items with attachments and export
        exported = 0
        failed = 0
        skipped = 0

        for item in items:
            title = item['data']['title']

            # Check for attachment
            links = item.get('links', {})
            if 'attachment' not in links:
                if verbose:
                    print(f"⊘ Skipped (no attachment): {title}")
                skipped += 1
                continue

            # Get attachment key from the attachment URL
            attachment_url = links['attachment']['href']
            attachment_key = attachment_url.split('/')[-1]

            # Generate filename based on naming mode
            filename = get_filename(item, naming_mode)
            output_path = output_dir / filename

            # Download PDF using attachment key
            try:
                client.download_file(attachment_key, output_path)
                if verbose:
                    pmid = extract_pmid(item)
                    pmid_str = f" (PMID: {pmid})" if pmid else ""
                    print(f"✓ Exported: {title}{pmid_str} -> {filename}")
                exported += 1
            except Exception as e:
                if verbose:
                    print(f"✗ Failed: {title} - {e}")
                failed += 1

        # Summary
        print("\n" + "=" * 50)
        print(f"Export Summary:")
        print(f"  Exported: {exported}")
        print(f"  Skipped: {skipped}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(items)}")
        print("=" * 50)

    if __name__ == "__main__":
        parser = argparse.ArgumentParser(
            description="Batch export PDFs from Zotero collection",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Naming Options:
  pmid      Use PMID as filename (default): {pmid}.pdf
  title     Use paper title: {title}.pdf
  doi       Use DOI: {doi}.pdf
  combined  Combined: {pmid}_{title}.pdf or {title}.pdf if no PMID

Examples:
  # Export with PMID naming (default)
  %(prog)s "My Collection" /path/to/output

  # Export with title naming
  %(prog)s "My Collection" /path/to/output --naming title

  # Export with DOI naming
  %(prog)s "My Collection" /path/to/output --naming doi
            """
        )
        parser.add_argument(
            "collection",
            help="Name of the Zotero collection"
        )
        parser.add_argument(
            "output",
            type=Path,
            help="Output directory for PDFs"
        )
        parser.add_argument(
            "-n", "--naming",
            choices=['pmid', 'title', 'doi', 'combined'],
            default='pmid',
            help="PDF naming mode (default: pmid)"
        )
        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            help="Suppress per-item output"
        )

        args = parser.parse_args()

        batch_export(args.collection, args.output, naming_mode=args.naming, verbose=not args.quiet)

except ImportError as e:
    print(f"\n✗ Import failed: {e}")
    print("\nPlease install zoteroapi:")
    print("  pip install zoteroapi")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\nExport cancelled by user")
    sys.exit(0)
