from __future__ import annotations

import time
import traceback
from typing import List, Optional
from urllib.parse import quote_plus

import chromedriver_autoinstaller
import xlwings as xw
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


SEARCH_QUERY = "bio nanocomposites for food packaging elsevier"
SEARCH_URL_TEMPLATE = (
    "https://scholar.google.com/scholar?start={start}&q={query}"
    "&hl=en&as_sdt=0,5&as_ylo=2017&as_yhi=2024"
)

RESULTS_PER_PAGE = 10
MAX_RESULTS = 100
START_ROW = 181

EXCEL_PATH = r"C:\Users\Acer\Downloads\Research.xlsx"
SHEET_NAME = "Sheet1"

RESULT_LINK_XPATH = "/html/body/div/div[10]/div[2]/div[3]/div[2]/div/div/h3/a"
PUBLICATION_TITLE_XPATH = "//*[@id='publication-title']/a/span/span"
ARTICLE_TITLE_XPATH = "//*[@id='screen-reader-main-title']/span"
DOI_XPATH = "//*[@id='article-identifier-links']/a[1]/span/span"
PUBLICATION_DATE_XPATHS = [
    "//*[@id='publication']/div[2]/div/a",
    "//*[@id='publication']/div[2]/div[3]",
]
ABSTRACT_XPATH = "//*[contains(@class,'abstract author')]/div/p"
INTRODUCTION_XPATHS = [
    "//*[contains(@class,'Introduction')]/section/p",
    "//*[contains(@class,'Body')]/div/section/p",
]


def create_driver() -> webdriver.Chrome:
    """Create a Chrome driver configured for this scraper."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(options=options)
    driver.delete_all_cookies()
    driver.set_page_load_timeout(30)
    return driver


def build_search_url(start_index: int) -> str:
    """Build the Google Scholar search URL for a specific result offset."""
    return SEARCH_URL_TEMPLATE.format(
        start=start_index,
        query=quote_plus(SEARCH_QUERY),
    )


def wait_for_search_results(driver: webdriver.Chrome, timeout: int = 15) -> None:
    """Wait until a page of Scholar results has loaded."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.XPATH, RESULT_LINK_XPATH))
    )


def first_non_empty_text(
    driver: webdriver.Chrome,
    xpaths: List[str],
    timeout: int = 5,
) -> str:
    """Return the first non-empty text value found from the provided XPaths."""
    for xpath in xpaths:
        try:
            text = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            ).text.strip()
            if text:
                return text
        except TimeoutException:
            continue
    return ""


def all_text_from_xpath(driver: webdriver.Chrome, xpath: str) -> str:
    """Collect and join all non-empty text from matching elements."""
    elements = driver.find_elements(By.XPATH, xpath)
    texts = [
        element.text.strip()
        for element in elements
        if element.text and element.text.strip()
    ]
    return " ".join(texts)


def get_article_data(driver: webdriver.Chrome) -> Optional[dict]:
    """Extract article metadata from the current Elsevier article page."""
    try:
        publication_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, PUBLICATION_TITLE_XPATH))
        ).text.strip()
    except TimeoutException:
        return None

    article_title = first_non_empty_text(driver, [ARTICLE_TITLE_XPATH])
    doi = first_non_empty_text(driver, [DOI_XPATH])
    publication_date = first_non_empty_text(driver, PUBLICATION_DATE_XPATHS)
    abstract_text = all_text_from_xpath(driver, ABSTRACT_XPATH)

    introduction_text = ""
    for xpath in INTRODUCTION_XPATHS:
        introduction_text = all_text_from_xpath(driver, xpath)
        if introduction_text:
            break

    return {
        "publication_title": publication_title,
        "article_title": article_title,
        "publication_date": publication_date,
        "doi": doi,
        "abstract": abstract_text,
        "introduction": introduction_text,
        "article_url": driver.current_url,
    }


def write_article_to_excel(sheet, row_number: int, article_data: dict) -> None:
    """Write one scraped article record into the spreadsheet."""
    sheet.range(f"B{row_number}").value = [
        article_data["publication_title"],
        article_data["article_title"],
        article_data["publication_date"],
        article_data["doi"],
        article_data["abstract"],
        article_data["introduction"],
        article_data["article_url"],
    ]


def process_search_page(
    driver: webdriver.Chrome,
    sheet,
    start_index: int,
    row_number: int,
) -> int:
    """Process one Scholar results page and append extracted records to Excel."""
    driver.get(build_search_url(start_index))
    wait_for_search_results(driver)

    results = driver.find_elements(By.XPATH, RESULT_LINK_XPATH)
    print(f"Start index {start_index}: found {len(results)} results")

    for result_index in range(len(results)):
        try:
            wait_for_search_results(driver)
            results = driver.find_elements(By.XPATH, RESULT_LINK_XPATH)

            if result_index >= len(results):
                break

            result = results[result_index]
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                result,
            )
            time.sleep(1)
            result.click()

            article_data = get_article_data(driver)
            if not article_data:
                driver.back()
                wait_for_search_results(driver)
                continue

            print(f"Publication: {article_data['publication_title']}")
            print(f"Title: {article_data['article_title']}")
            print(f"Date: {article_data['publication_date']}")
            print(f"DOI: {article_data['doi']}")

            write_article_to_excel(sheet, row_number, article_data)
            row_number += 1

            driver.back()
            wait_for_search_results(driver)

        except Exception:
            print(traceback.format_exc())
            try:
                driver.back()
                wait_for_search_results(driver)
            except Exception:
                pass

    return row_number


def main() -> None:
    chromedriver_autoinstaller.install()
    driver = create_driver()

    app = None
    workbook = None
    current_row = START_ROW

    try:
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False

        workbook = app.books.open(EXCEL_PATH)
        sheet = workbook.sheets[SHEET_NAME]

        for start_index in range(0, MAX_RESULTS, RESULTS_PER_PAGE):
            current_row = process_search_page(driver, sheet, start_index, current_row)
            workbook.save()

    finally:
        if workbook is not None:
            workbook.close()
        if app is not None:
            app.quit()
        driver.quit()


if __name__ == "__main__":
    main()
