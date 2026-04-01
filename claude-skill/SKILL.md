---
name: zoteroapi
description: Search and export papers from Zotero local library. Use when user asks to search Zotero by PMID/DOI/keywords, download PDFs from Zotero, export metadata, or batch process papers from their local Zotero library. Independent skill - no external dependencies.
---

# ZoteroAPI Client Skill

This skill provides comprehensive access to Zotero local library through the zoteroapi Python package. It enables searching, retrieving metadata, and exporting PDFs from your local Zotero database.

## Prerequisites

**Zotero Local Server Requirements:**
- Zotero desktop application must be **running**
- Local server enabled:
  1. Open Zotero Preferences
  2. Advanced → Config Editor
  3. Set `extensions.zotero.httpServer.enabled = true`
  4. Restart Zotero
- Default port: 23119
- No authentication required for local access

**Python Package:**
```bash
# Install zoteroapi (if not already installed)
pip install zoteroapi

# Or install in development mode from source
cd /path/to/zoteroapi
pip install -e .
```

## When to Activate

Activate this skill when the user asks to:
- Search Zotero library by PMID, DOI, title, or keywords
- Download/export PDFs from their Zotero library
- Get paper metadata from Zotero
- Batch process multiple papers from Zotero
- Export collections or items from Zotero

**Keywords:** zotero, PMID, DOI, search papers, export PDF, local library

## Core API Methods

### Search Methods

#### search_by_pmid(pmid: str)
Search Zotero library by PubMed ID.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
results = client.search_by_pmid("12345678")

if results:
    item = results[0]
    title = item['data']['title']
    print(f"Found: {title}")
else:
    print("Not found in library")
```

**Note:** The skill supports both newer Zotero versions with a dedicated `PMID` field and older versions where PMID is stored in the `extra` field as `PMID: xxxxxxxx`

#### search_by_doi(doi: str)
Search Zotero library by DOI.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
results = client.search_by_doi("10.1038/nature12373")

if results:
    print(f"Found: {results[0]['data']['title']}")
```

#### search_items(query: str)
Search Zotero library by keywords.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
results = client.search_items("machine learning")
print(f"Found {len(results)} papers")
```

#### search_by_title(title: str, exact_match: bool = False)
Search by paper title.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# Fuzzy search (default)
results = client.search_by_title("深度学习")

# Exact match
results = client.search_by_title("Machine Learning Basics", exact_match=True)
```

### Retrieval Methods

#### get_item(item_key: str)
Get complete item metadata by key.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
item = client.get_item("ABC123XYZ")

# Access metadata
title = item['data']['title']
authors = item['data']['creators']
doi = item['data'].get('DOI', '')
pmid = client.get_pmid("ABC123XYZ")

print(f"Title: {title}")
print(f"Authors: {[a['name'] for a in authors]}")
print(f"DOI: {doi}")
print(f"PMID: {pmid}")
```

#### get_items(limit: Optional[int] = None)
Get all items from library.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# Get first 50 items
items = client.get_items(limit=50)

# Get all items (may be slow for large libraries)
all_items = client.get_items()
```

#### get_items_top(limit: int = 10)
Get top-level items (excludes notes/attachments).

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
items = client.get_items_top(limit=20)
```

### File Export Methods

#### download_file(item_key: str, path: Union[str, Path])
Download attached PDF to specified path.

```python
from zoteroapi import ZoteroLocal
from pathlib import Path

client = ZoteroLocal()

# Download to user-specified location
output_path = Path.home() / "Downloads" / "paper.pdf"
client.download_file("ABC123XYZ", output_path)
print(f"Downloaded to {output_path}")
```

**Important:**
- The item must have an attached PDF
- Parent directories are created automatically
- Path is specified by user (no default location)

#### get_item_file(item_key: str)
Get file as binary stream.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
file_content = client.get_item_file("ABC123XYZ")

# Save to custom location
with open("output.pdf", "wb") as f:
    f.write(file_content.read())
```

### Collection Methods

#### get_collections()
Get all collections.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
collections = client.get_collections()

for coll in collections:
    name = coll['data']['name']
    num_items = coll['data'].get('numItems', 0)
    print(f"{name}: {num_items} papers")
```

#### get_collection_items(collection_key: str)
Get all items in a collection.

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
items = client.get_collection_items("COLLECTION_KEY")
```

## Batch Processing

### Batch Search by PMIDs

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

pmids = ["12345678", "23456789", "34567890"]

found_items = []
for pmid in pmids:
    results = client.search_by_pmid(pmid)
    if results:
        found_items.extend(results)
        print(f"✓ Found PMID {pmid}: {results[0]['data']['title']}")
    else:
        print(f"✗ PMID {pmid} not found in library")

print(f"\nFound {len(found_items)} of {len(pmids)} papers")
```

### Batch Export PDFs

```python
from zoteroapi import ZoteroLocal
from pathlib import Path

client = ZoteroLocal()

# User-specified output directory
output_dir = Path("/path/to/output/directory")
output_dir.mkdir(parents=True, exist_ok=True)

item_keys = ["KEY1", "KEY2", "KEY3"]

for key in item_keys:
    try:
        # Get item metadata
        item = client.get_item(key)
        title = item['data']['title']

        # Create safe filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        output_path = output_dir / f"{safe_title}.pdf"

        # Download PDF
        client.download_file(key, output_path)
        print(f"✓ Downloaded: {title}")

    except Exception as e:
        print(f"✗ Failed to download {key}: {e}")
```

### Batch Search and Export

```python
from zoteroapi import ZoteroLocal
from pathlib import Path

client = ZoteroLocal()

# Search criteria
query = "machine learning"
results = client.search_items(query)

# User-specified output directory
output_dir = Path("/path/to/output/directory")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Found {len(results)} papers matching '{query}'")

# Export each paper's PDF
for item in results:
    try:
        key = item['key']
        title = item['data']['title']

        # Check if item has attachments
        links = item.get('links', {})
        if 'attachment' in links:
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            output_path = output_dir / f"{safe_title}.pdf"

            client.download_file(key, output_path)
            print(f"✓ Exported: {title}")
        else:
            print(f"⊘ No attachment: {title}")

    except Exception as e:
        print(f"✗ Failed: {item['data']['title']} - {e}")
```

## Common Workflows

### Workflow 1: Search by PMID and Export PDF

```python
from zoteroapi import ZoteroLocal
from pathlib import Path

client = ZoteroLocal()
pmid = "12345678"

# Step 1: Search by PMID
results = client.search_by_pmid(pmid)

if not results:
    print(f"PMID {pmid} not found in Zotero library")
    exit()

item = results[0]
title = item['data']['title']
print(f"Found: {title}")

# Step 2: Get DOI if available
doi = item['data'].get('DOI', 'N/A')
print(f"DOI: {doi}")

# Step 3: Download PDF to user-specified location
output_path = Path.home() / "Downloads" / f"{pmid}_{title[:50]}.pdf"
client.download_file(item['key'], output_path)
print(f"Downloaded to: {output_path}")
```

### Workflow 2: Search by DOI and Get Metadata

```python
from zoteroapi import ZoteroLocal
import json

client = ZoteroLocal()
doi = "10.1038/nature12373"

# Search by DOI
results = client.search_by_doi(doi)

if results:
    item = results[0]

    # Extract metadata
    metadata = {
        'key': item['key'],
        'title': item['data']['title'],
        'authors': [c['name'] for c in item['data'].get('creators', [])],
        'publication': item['data'].get('publicationTitle', ''),
        'year': item['data'].get('date', ''),
        'doi': item['data'].get('DOI', ''),
        'abstract': item['data'].get('abstractNote', ''),
        'tags': [t['tag'] for t in item['data'].get('tags', [])]
    }

    # Pretty print
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
else:
    print(f"DOI {doi} not found in library")
```

### Workflow 3: Export Collection PDFs

```python
from zoteroapi import ZoteroLocal
from pathlib import Path

client = ZoteroLocal()

# Get collection
collection_name = "My Research"
collections = client.get_collections()

# Find collection by name
target_collection = None
for coll in collections:
    if coll['data']['name'] == collection_name:
        target_collection = coll
        break

if not target_collection:
    print(f"Collection '{collection_name}' not found")
    exit()

# Get items in collection
items = client.get_collection_items(target_collection['key'])

# User-specified output directory
output_dir = Path.home() / "Downloads" / collection_name
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Exporting {len(items)} items from '{collection_name}'")

for item in items:
    try:
        # Check for PDF attachment
        links = item.get('links', {})
        if 'attachment' not in links:
            continue

        title = item['data']['title']
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        output_path = output_dir / f"{safe_title}.pdf"

        client.download_file(item['key'], output_path)
        print(f"✓ {title}")

    except Exception as e:
        print(f"✗ Failed: {item['data']['title']} - {e}")
```

## Error Handling

### Basic Error Handling

```python
from zoteroapi import ZoteroLocal, ZoteroLocalError, ResourceNotFound

client = ZoteroLocal()

try:
    item = client.get_item("INVALID_KEY")
except ResourceNotFound:
    print("Item not found in library")
except ZoteroLocalError as e:
    print(f"Error: {e}")
```

### Robust Batch Processing

```python
from zoteroapi import ZoteroLocal, ZoteroLocalError

client = ZoteroLocal()
pmids = ["12345678", "23456789", "34567890"]

results = {
    'found': [],
    'not_found': [],
    'errors': []
}

for pmid in pmids:
    try:
        items = client.search_by_pmid(pmid)
        if items:
            results['found'].append({'pmid': pmid, 'item': items[0]})
        else:
            results['not_found'].append(pmid)
    except ZoteroLocalError as e:
        results['errors'].append({'pmid': pmid, 'error': str(e)})

# Summary
print(f"Found: {len(results['found'])}")
print(f"Not found: {len(results['not_found'])}")
print(f"Errors: {len(results['errors'])}")
```

## Item Data Structure

Each item returned by the API has this structure:

```python
{
    'key': 'ABC123XYZ',              # Unique item identifier
    'version': 1234,                  # Item version
    'data': {                         # Core metadata
        'title': 'Paper Title',
        'creators': [                 # Authors/Editors
            {'creatorType': 'author', 'name': 'Author Name'},
            # ...
        ],
        'abstractNote': 'Abstract text',
        'publicationTitle': 'Journal Name',
        'volume': '10',
        'issue': '1',
        'pages': '1-10',
        'date': '2024',
        'DOI': '10.1234/example',
        'PMID': '12345678',            # Dedicated PMID field (newer Zotero versions)
        'extra': 'PMID: 12345678\nOther info',  # Or in extra field (older Zotero)
        'tags': [{'tag': 'keyword1'}, {'tag': 'keyword2'}],
        'itemType': 'journalArticle'
    },
    'meta': {                         # Metadata
        'createdByUser': {'id': 1, 'name': 'User', 'username': 'user'}
    },
    'links': {                        # Related links
        'attachment': {               # If has attachment
            'attachmentType': 'application/pdf',
            'href': 'http://...'
        }
    }
}
```

**Note on PMID:** The skill automatically checks for PMID in both the dedicated `PMID` field (newer Zotero versions) and the `extra` field (older versions).

## Testing Your Setup

### Test Connection

```python
from zoteroapi import ZoteroLocal

try:
    client = ZoteroLocal()
    items = client.get_items_top(limit=1)
    print(f"✓ Connected! Found {len(items)} top-level items")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure Zotero desktop app is running")
    print("2. Enable local server: Edit > Preferences > Advanced > Config Editor")
    print("3. Set extensions.zotero.httpServer.enabled = true")
    print("4. Restart Zotero")
```

### Test PMID Search

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# First, check if you have any items with PMID
items = client.get_items(limit=100)

pmid_items = []
for item in items:
    # Check for PMID in dedicated field (newer Zotero) or extra field (older Zotero)
    pmid = item.get('data', {}).get('PMID')
    if not pmid:
        extra = item.get('data', {}).get('extra', '')
        for line in extra.split('\n'):
            if line.startswith('PMID:'):
                pmid = line.split(':', 1)[1].strip()
                break
    if pmid:
        pmid_items.append(item)

if pmid_items:
    print(f"Found {len(pmid_items)} items with PMID")
    # Get PMID from first item
    pmid = pmid_items[0].get('data', {}).get('PMID')
    if not pmid:
        extra = pmid_items[0]['data'].get('extra', '')
        for line in extra.split('\n'):
            if line.startswith('PMID:'):
                pmid = line.split(':', 1)[1].strip()
                break

    # Test search
    results = client.search_by_pmid(pmid)
    if results:
        print(f"✓ PMID search working! Found: {results[0]['data']['title']}")
else:
    print("No items with PMID found in library")
    print("Tip: Add PMID to item's dedicated 'PMID' field or 'Extra' field as 'PMID: 12345678'")
```

## Available Scripts

All scripts are located in `~/.claude/skills/zoteroapi/scripts/` directory:

### Main Scripts

| Script | Purpose |
|--------|---------|
| `scripts/zotero_search.py` | Universal search tool - search by PMID/DOI/keywords/title, export as JSON (CLI + Python API) |
| `scripts/query_by_pmid.py` | Query paper information by PMID (supports table, JSON, Markdown formats) |
| `scripts/batch_export.py` | Batch export PDFs from Zotero collection |
| `scripts/test_connection.py` | Test Zotero local server connection |
| `scripts/test_search.py` | Test search functionality |

### PMID Query Script

The `query_by_pmid.py` script searches Zotero for papers by their PMID and outputs detailed information.

**Usage:**
```bash
# Query single PMID (table format - default)
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py 39122952

# Query multiple PMIDs
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py 39122952 40931188 6305503

# Include abstract, tags, and attachment info
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py 39122952 --verbose

# Output as Markdown
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py 39122952 --format markdown

# Output as JSON and save to file
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py 39122952 --format json --output results.json

# Read PMIDs from file (one per line)
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py --file pmids.txt
```

**Output Formats:**

| Format | Description | Use Case |
|--------|-------------|----------|
| `table` (default) | Formatted table using tabulate | Terminal viewing, quick reference |
| `json` | Structured JSON data | Programmatic processing, data export |
| `markdown` | Markdown format with DOI links | Documentation, notes, Obsidian/Logseq |

**Output Fields (varies by format):**
- PMID
- Title
- Authors (formatted: "Author1, Author2, Author3 et al.")
- Journal
- Year
- Volume, Issue, Pages
- DOI
- Abstract (verbose mode only)
- Tags (verbose mode only)
- Attachment status (verbose mode only)

**Options:**
- `--format`, `-F`: Output format (table, json, markdown)
- `--verbose`, `-v`: Include abstract, tags, and attachment info
- `--output`, `-o`: Save output to file (JSON format only)
- `--file`, `-f`: Read PMIDs from file

### Batch Export Script

The `batch_export.py` script exports all PDFs from a Zotero collection to a specified directory with customizable naming.

**Usage:**
```bash
# Basic usage (default PMID naming)
python ~/.claude/skills/zoteroapi/scripts/batch_export.py "Collection Name" /path/to/output

# With title naming
python ~/.claude/skills/zoteroapi/scripts/batch_export.py "Collection Name" /path/to/output --naming title

# With DOI naming
python ~/.claude/skills/zoteroapi/scripts/batch_export.py "Collection Name" /path/to/output --naming doi

# Combined naming (PMID + title, fallback to title if no PMID)
python ~/.claude/skills/zoteroapi/scripts/batch_export.py "Collection Name" /path/to/output --naming combined

# Quiet mode (suppress per-item output)
python ~/.claude/skills/zoteroapi/scripts/batch_export.py "Collection Name" /path/to/output -q
```

**Naming Options:**

| Option | Description | Example Filename |
|--------|-------------|------------------|
| `pmid` (default) | Use PMID as filename | `12345678.pdf` |
| `title` | Use paper title (sanitized) | `Deep Learning Research.pdf` |
| `doi` | Use DOI (slashes replaced with underscores) | `10.1038_nature12373.pdf` |
| `combined` | PMID + title (truncated to 50 chars) | `12345678_Deep Learning Research.pdf` |

**Fallback Behavior:**
- If `pmid` mode and no PMID found → Falls back to title
- If `doi` mode and no DOI found → Falls back to title
- If `combined` mode and no PMID found → Uses title only

### Universal Search Script (zotero_search.py)

The `zotero_search.py` script provides a unified interface to search Zotero by various methods (PMID, DOI, keywords, title) and export results in structured JSON format. It supports both command-line and Python API usage.

**Command-line Usage:**
```bash
# Search by PMID
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --pmid 12345678 --output results.json

# Search by DOI
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --doi "10.1038/nature12373" --output results.json

# Search by keywords
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --search "machine learning" --output results.json

# Search by title
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --title "Deep Learning" --output results.json

# Limit results
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --search "transformers" --limit 10 --output results.json

# Exact title match
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --title "Attention Is All You Need" --exact --output results.json

# Output to stdout (pretty printed)
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --search "finetune" --pretty

# Compact JSON output
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --search "machine learning" --no-pretty
```

**Python API Usage:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('~/.claude/skills/zoteroapi/scripts').expanduser()))

from zotero_search import ZoteroSearch

searcher = ZoteroSearch()

# Search by keywords
results = searcher.search_by_keyword("machine learning", limit=10)

# Search by PMID
results = searcher.search_by_pmid("12345678")

# Search by DOI
results = searcher.search_by_doi("10.1038/nature12373")

# Search by title (fuzzy or exact)
results = searcher.search_by_title("Deep Learning", exact_match=False)

# Generic search
results = searcher.search("keyword", "machine learning")
```

**JSON Output Format:**
```json
[
  {
    "key": "ABC123XYZ",
    "pmid": "12345678",
    "doi": "10.1038/nature12373",
    "title": "Paper Title",
    "authors": ["Author1", "Author2"],
    "abstract": "Abstract text",
    "journal": "Journal Name",
    "volume": "10",
    "issue": "1",
    "pages": "1-10",
    "date": "2024",
    "year": "2024",
    "tags": ["tag1", "tag2"],
    "has_attachment": true,
    "item_type": "journalArticle",
    "url": ""
  }
]
```

**Options:**
- `--pmid`: Search by PMID
- `--doi`: Search by DOI
- `--search`, `-s`: Search by keywords
- `--title`: Search by title
- `--output`, `-o`: Save output to file (if not specified, prints to stdout)
- `--limit`, `-l`: Limit number of results (for keyword search)
- `--pretty`, `-p`: Pretty print JSON (default: True)
- `--no-pretty`: Disable pretty printing (compact JSON)
- `--exact`: Use exact match for title search

**Use Cases:**
- Data source for other tools/scripts
- Batch processing with structured output
- Integration with pipelines
- Programmatic access via Python API

### PMID Query Script

**Test Connection:**
```bash
python ~/.claude/skills/zoteroapi/scripts/test_connection.py
```

**Test Search:**
```bash
python ~/.claude/skills/zoteroapi/scripts/test_search.py
```

## Limitations

1. **Local Only**: Only searches your local Zotero library, not online databases
2. **Read-Only**: Cannot create new items or modify existing ones (query only)
3. **PMID Format**: Supports both dedicated `PMID` field (newer Zotero) and `extra` field format (older Zotero)
4. **Attachments**: Can only download files that are already attached to items
5. **Zotero Required**: Zotero desktop app must be running with local server enabled

## Example Interactions

**User**: "Search my Zotero library for PMID 12345678"
**You**:
```python
from zoteroapi import ZoteroLocal
client = ZoteroLocal()
results = client.search_by_pmid("12345678")
if results:
    print(f"Found: {results[0]['data']['title']}")
else:
    print("Not found in library")
```

**User**: "Download all PDFs from my 'Machine Learning' collection"
**You**:
```python
from zoteroapi import ZoteroLocal
from pathlib import Path

client = ZoteroLocal()
collections = client.get_collections()

# Find the collection
ml_collection = next((c for c in collections if c['data']['name'] == 'Machine Learning'), None)

if ml_collection:
    items = client.get_collection_items(ml_collection['key'])
    output_dir = Path.home() / "Downloads" / "Machine Learning"
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in items:
        if 'attachment' in item.get('links', {}):
            try:
                title = item['data']['title']
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                client.download_file(item['key'], output_dir / f"{safe_title}.pdf")
                print(f"✓ Downloaded: {title}")
            except Exception as e:
                print(f"✗ Failed: {title} - {e}")
else:
    print("Collection 'Machine Learning' not found")
```

**User**: "Batch search these PMIDs: 12345678, 23456789, 34567890"
**You**:
```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
pmids = ["12345678", "23456789", "34567890"]

for pmid in pmids:
    results = client.search_by_pmid(pmid)
    if results:
        item = results[0]
        print(f"{pmid}: {item['data']['title']}")
    else:
        print(f"{pmid}: Not found")
```

**User**: "Query PMID 39122952 and show detailed information"
**You**:
```bash
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py 39122952 --verbose
```

**User**: "Get information for multiple PMIDs in JSON format"
**You**:
```bash
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py 39122952 40931188 --format json --output papers.json
```

**User**: "Query PMIDs and export as Markdown for my notes"
**You**:
```bash
python ~/.claude/skills/zoteroapi/scripts/query_by_pmid.py 39122952 40931188 --format markdown
```

**User**: "Search Zotero for papers about 'transformers' and export as JSON"
**You**:
```bash
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --search "transformers" --limit 20 --output transformers.json
```

**User**: "Get paper data by PMID for use in another script"
**You**:
```bash
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --pmid 39122952 --no-pretty | jq '.'
```

**User**: "Search by DOI and get structured data"
**You**:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('~/.claude/skills/zoteroapi/scripts').expanduser()))

from zotero_search import ZoteroSearch

searcher = ZoteroSearch()
papers = searcher.search_by_doi("10.1038/nature12373")

for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"Journal: {paper['journal']} ({paper['year']})")
    print(f"DOI: {paper['doi']}")
```

**User**: "Find papers with 'attention' in the title"
**You**:
```bash
python ~/.claude/skills/zoteroapi/scripts/zotero_search.py --title "attention" --limit 10 --output attention_papers.json
```
