# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python testing tool for the Shanghai Library Open Data API. It automatically tests 90+ API endpoints across multiple categories (general resources, PDFs, stone rubbings, films, ancient books, family records, etc.), saves successful responses, and logs errors for analysis.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Get API key from: https://data.library.sh.cn/key

# Set API key (choose one method)
# Linux/macOS:
export SHANGHAI_LIBRARY_API_KEY=your_key_here

# Windows (Command Prompt):
set SHANGHAI_LIBRARY_API_KEY=your_key_here

# Windows (PowerShell):
$env:SHANGHAI_LIBRARY_API_KEY="your_key_here"

# OR edit config.py directly

# Run all API tests
python main.py

# Generate statistics on API results
python file_stats.py
```

## Architecture

### Core Components

**main.py** - Entry point and orchestrator
- Prints banner and manages test execution flow
- Handles keyboard interrupts and exceptions
- Calls `run_tests()` to execute all API tests

**api_lists.py** - API definitions repository
- Contains `API_DEFINITIONS` list with 90+ API endpoints
- Each endpoint defines: name, method, URL, params, special handling
- Categories: [通用], [PDF], [碑帖], [电影], [古籍], [家谱], etc.
- `get_all_apis()` function returns all API definitions

**api_client.py** - HTTP client module
- `APIClient` class handles all HTTP requests
- Supports GET and POST methods
- Handles JSON responses and file downloads (PDFs)
- Implements request delays to avoid rate limiting
- Saves successful responses to `api_results/` directory
- Logs errors to `log/error_log.json`

**config.py** - Centralized configuration
- API key management (environment variable + fallback)
- Output directory settings
- HTTP headers and request delays
- Terminal color codes for output formatting

**utils.py** - Utility functions
- File sanitization for safe filenames
- Directory creation
- Response size formatting
- JSON error logging

**file_stats.py** - Statistics generator
- Analyzes `api_results/` directory for file counts and sizes
- Generates statistics by API category and file type
- Lists largest files
- Saves analysis to `api_results_stats.json`

### Data Flow

```
main.py → get_all_apis() → run_tests() → run_api_test() → APIClient.make_request()
                                           ↓
                                    Save results or log errors
```

## Configuration

**API Key Priority:**
1. Environment variable `SHANGHAI_LIBRARY_API_KEY`
2. `API_KEY` variable in `config.py`

**Key Settings in config.py:**
- `OUTPUT_DIR`: Directory for successful API responses (default: `api_results/`)
- `LOG_FILE`: Error log file path (default: `log/error_log.json`)
- `DELAY_SECONDS`: Rate limiting delay between requests (default: 2)
- `HEADERS`: HTTP headers for API requests

## Output Structure

- **api_results/** - Successful API responses, organized by category
  - JSON responses saved with descriptive filenames
  - PDF files downloaded when applicable
- **log/error_log.json** - Error log with timestamps, API names, and error details

## Adding New APIs

To add new API endpoints, edit `api_lists.py` and add to the `API_DEFINITIONS` list:

```python
{
    "name": "API Display Name",
    "method": "GET",  # or "POST"
    "url": "endpoint_path",
    "params": {"key": "value"},  # optional
    "save_as_pdf": False,  # optional, for PDF downloads
    "category": "[分类]"  # category tag for organization
}
```

## Dependencies

- Python 3.6+
- requests>=2.28.0

## Notes

- No build, test, or lint commands are configured - this is a simple Python script
- The application handles rate limiting with 2-second delays between requests
- Keyboard interrupts (Ctrl+C) are gracefully handled
- Filenames are sanitized to avoid filesystem issues
