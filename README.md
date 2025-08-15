# AbSearch

AbSearch is a command-line tool to search antibody vendors for antibodies targeting a given protein, then filter results by criteria such as species reactivity, host, clonality, applications, conjugation, citations, and price.

This repo is scaffolded with a modular provider architecture so new vendor scrapers can be added easily.

## Quick start

```bash
# Create and activate a virtualenv (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the CLI (example)
python -m absearch.cli "TP53" --applications WB IHC --clonality monoclonal --species-reactivity Human Mouse --json
```

## Features
- Provider interface to add vendor-specific search/scrape modules
- Concurrent querying of providers
- Unified antibody data model
- Flexible filtering by structured criteria
- Output as a rich table, JSON, or CSV

## Project structure
```
absearch/
  cli.py             # CLI entry point
  search.py          # Orchestrates provider queries
  filters.py         # Applies user criteria to results
  models.py          # Pydantic models for Antibody and Criteria
  providers/
    base.py          # Provider protocol
    abcam.py         # Example provider stub
    cst.py           # Example provider stub
```

## Adding a provider
1. Create a file under `absearch/providers/your_vendor.py` implementing `AntibodyProvider`.
2. Export it in `absearch/providers/__init__.py` or register it in `absearch/search.py`.
3. Parse results into `AntibodyRecord` objects.

## Notes
- Some vendor sites use dynamic rendering or bot protection. You may need to use headers, delays, retries, or alternative endpoints.
- Respect each site's robots.txt and terms of service.
- This scaffold does not yet implement specific vendors; add the websites you need and criteria to enable end-to-end results.
