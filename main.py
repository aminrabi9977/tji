from playwright.sync_api import sync_playwright
import time
from langchain_openai import ChatOpenAI
with sync_playwright() as p:
    browser = p.chromium.launch(headless = False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.isna.ir/')
    print(page.title())
    
    page.click('a[href="/service/Science-Academia"]')
    # page.wait_for_timeout(3000)
    time.sleep(3)

    # Select the "Latest News" section and click the first news item
    # first_news_selector = '#box17 ul li:first-child h3 a'  # Adjusted for the specific section
    # page.click(first_news_selector)
    # page.wait_for_timeout(3000)
    # with context.expect_page() as new_tab_info:
    with page.expect_popup() as pop_info: 
        page.click('#box17 ul li:first-child h3 a[target="_blank"]') 
        print('ok') # Click on the first news item
    page1 = pop_info.value    
    title = page1.locator('h1.first-title').inner_text()
    summary = page1.locator('div p.summary').inner_text()
    # print(summary)
    
    paragraphs = page1.query_selector_all('div.item-text p')
    paragraphs_form_second = paragraphs[0:]
    txt = ""
    for paragraph in paragraphs_form_second:
        txt += paragraph.inner_text() + '\n'

        
        time.sleep(3)

         
    context.close()
    # page.wait_for_timeout(3000)
    browser.close()

# # Set your API key  
  # pip install -U langchain_openai
all_text = f'title: {title}\nsummary: {summary}\ncontent: {txt}'
llm = ChatOpenAI(
    model="gpt-4o-mini",
    base_url="https://api.avalai.ir/v1", 
    api_key="aa-NaiWnOnrIVzanEH5frUbwkCnmoyBzXHE7FYBBXmgfqzlEduf"
)

res = llm.invoke(f"""
 
I have a piece of news written in the format of title, summary, and content, stored in the all_text variable. Here is the original text:
                 {all_text}
Your task is to assist me in republishing this news for another news site by performing the following steps:  

1. Translate the original news text into **Persian**.  
2. Ensure the translated text is **different in wording and style** from the original, while retaining the exact same meaning and message.  
3. Present the translated text in the following format:  
   - **title:** [Persian translation of the title, rewritten uniquely]  
   - **summary:** [Persian translation of the summary, rewritten uniquely]  
   - **content:** [Persian translation of the content, rewritten uniquely]  
4. Generate a list of **SEO-friendly keywords** in Persian, designed specifically to appeal to Iranian users searching for this topic. Include terms that are both commonly used and contextually relevant to the news content.  

The output should follow this structure:  
- title:  
- summary:  
- content:  
- keywords:"  

--- 
 

                 """)
print(res.content) 

# # Print the assistant's response  
# print(response['choices'][0]['message']['content'])  

 
    # newtab = new_tab_info.value
    # print(new_tab)  # Get the new tab object
   
    # Wait for the new tab to load
    # new_tab.wait_for_load_state('load')
 
    # # Print the title of the new tab (news page)
    # print("News Page Title:", new_tab.title())
    
    # time.sleep(2)
    # print("News Page Title:", page.title())
    # title = title_element.inner_text() if title_element else "Title not found"
    # print("\nTitle:")
    # print(title)

    # # Extract the summary
    # summary = page.locator('p.summary').inner_text()
    # print("\nSummary:")
    # print(summary)
    # Extract the text inside the h1 element
    # h1_selector = 'p.summary'
    # page.wait_for_selector(h1_selector, timeout=60000)  # Wait up to 60 seconds

    # h1_text =  page.locator(h1_selector).inner_text()
    # print("H1 Text:", h1_text)


    # headline = page.text_content('h1.first-title[itemprop="headline"]')

    # print(headline)            
                # Now you can continue with your Google automation
                # For example, perform a search:
    # page.fill('textarea[name="q"]', 'playwright python')
    # page.press('textarea[name="q"]', 'Enter')
                
                # Wait to see the search results
