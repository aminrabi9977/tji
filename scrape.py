from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import List  # اضافه شده برای استفاده از تایپ‌های generic

def remove_unwanted_tag(html_content, unwanted_tags=["script", "style"]):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()
    return str(soup)

def extract_full_content(html_content, important_tags=["h1", "h2", "h3", "p", "article", "section"]):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_part = []
    for tag in important_tags:
        elements = soup.find_all(tag)
        for element in elements:
            cleaned_text = element.get_text().strip()
            if cleaned_text:  # فقط متون غیر تهی اضافه شوند
                if tag in ["h1", "h2", "h3"]:
                    text_part.append(f"[{tag.upper()}] {cleaned_text}")
                else:
                    text_part.append(cleaned_text)
    return "\n".join(text_part)

def extract_tags(html_content, tags: List[str]):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_parts = []
    for tag in tags:
        elements = soup.find_all(tag)
        for element in elements:
            if tag == "a":
                href = element.get('href')
                if href:
                    text_parts.append(f"{element.get_text()} ({href})")
                else:
                    text_parts.append(element.get_text())
            else:
                text_parts.append(element.get_text())
    return ' '.join(text_parts)

async def ascrape_playwright(url, tags: List[str] = ["h1", "h2", "h3", "span"]) -> str:
    print("Starting scrapin...")
    result = ""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_timeout(30000)
            page_sources = await page.content()
            soup = BeautifulSoup(page_sources, 'html.parser')
            
            for tag in ['script', 'style', 'noscript', 'iframe', 'svg', 'nav', 'footer', 'header']:
                for element in soup.find_all(tag):
                    element.decompose()
            
            news_contetn = []
            news_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '#article-content',
                '.story-content',
                'main',
                '[role="main"]',
                '.main-content',
                '.content-body',
                '.article-body'
            ]
            
            for selector in news_selectors:
                try:
                    news_element = soup.select(selector)
                    if news_element:
                        for element in news_element:
                            text = element.get_text(separator='\n', strip=True)
                            if text:
                                news_contetn.append(text)
                except Exception as e:
                    continue
                
            if not news_contetn:
                print("there is not news.")
                contetnt_parts = []
                for tag in ['h1', 'h2', 'h3', 'p', 'article', 'section', 'div.content']:
                    elements = soup.find_all(tag)
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text and len(text) > 40:
                            contetnt_parts.append(text)
                news_contetn = contetnt_parts
            
            result = '\n\n'.join(news_contetn)
            print("scraping is successful")
            if len(result) < 100:
                print("the page is dynamic or protected")
        except Exception as e:
            result = f"Error: {e}"
            print(f"error: {e}")
        finally:
            await browser.close()
    return result
