# Elsevier Data Scraper

A Python-based web scraping tool that automates the collection of academic research paper metadata from Elsevier journals via Google Scholar search results.

## Overview

This tool uses Selenium to navigate Google Scholar search results for a specific query (bio nanocomposites for food packaging, filtered to Elsevier publications from 2017-2024), clicks through to each paper's Elsevier page, and extracts structured metadata including the journal name, paper title, publication date, DOI, abstract, and introduction text. All extracted data is written directly into a local Excel spreadsheet using `xlwings`.

## Features

- Automated Google Scholar pagination (scrapes up to 100 results in pages of 10)
- Navigates to each individual Elsevier article page
- Extracts:
  - Journal / Publication name
  - Article title
  - Publication date
  - DOI
  - Abstract
  - Introduction text
  - Direct article URL
- Appends results row-by-row into a local Excel file (`Research.xlsx`)
- Handles missing fields gracefully with `try/except` fallbacks

## Requirements

- Python 3.x
- Google Chrome browser

### Python Dependencies

```
selenium
undetected-chromedriver
seleniumbase
chromedriver-autoinstaller
pandas
xlwings
```

Install all dependencies with:

```bash
pip install selenium undetected-chromedriver seleniumbase chromedriver-autoinstaller pandas xlwings
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Sumit3301/Elsavier-Data-scraper.git
   cd Elsavier-Data-scraper
   ```

2. Install dependencies (see above).

3. Open `app.py` and update the Excel file path to point to your local spreadsheet:
   ```python
   path = r"C:\path\to\your\Research.xlsx"
   ```

4. If needed, adjust the `GOOGLE_SCHOLAR_SEARCH_RESULT` URL to change the search query, year range, or other filters.

5. Set the `global_list_index` variable to the correct starting row in your Excel sheet (default is `181`).

## Usage

Run the scraper with:

```bash
python app.py
```

The script will open a Chrome browser window for each page of results, navigate to each article, extract the data, and save it to your Excel file before moving on to the next result.

Note: The script includes `time.sleep()` delays between actions to avoid rate-limiting and to allow pages to fully load. Do not reduce these without caution.

## Output

Data is written to a local Excel file. Each row contains the following columns (in order):

| Column | Description |
|--------|-------------|
| Publication | Journal / publisher name |
| Title | Article title |
| Date | Publication date |
| DOI | Digital Object Identifier |
| Abstract | Full abstract text |
| Introduction | Introduction section text |
| URL | Direct link to the article |

## Limitations

- The script is configured for a specific hardcoded search query; modifying it requires editing the `GOOGLE_SCHOLAR_SEARCH_RESULT` variable in `app.py`.
- The Excel file path is hardcoded and must be updated before running.
- Google Scholar may present CAPTCHAs or block automated access after extended use.
- Elsevier page structure changes may break the XPath selectors.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
