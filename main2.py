# import asyncio
# from typing import List
# from bs4 import BeautifulSoup
# from ai_extractor import ContentAnalyzer
# from schema import websiteReport
# from sctape import ascrape_playwright
# from auto_uploader import upload_playwright

# async def upload_republish_to_txtfile(reports):
#       with open("republished_news.txt" , "w" , encoding='utf-8') as f:
#         for report in reports:
            
#                     f.write("\n" + "="*50)
#                     f.write(f"\nTitle: {report.title}")
#                     f.write("\n" + "="*50)
#                     f.write("\nSummary:")
#                     f.write(report.summary)
#                     f.write("\n" + "="*50)
#                     f.write("\nContent:")
#                     f.write(report.content)   
#                     f.write("\n" + "="*50)
#                     f.write("\nHashtags:")
#                     f.write(report.hasgtag)
#                     f.write("\n" + "="*50)
#         return     
# urls = ["https://www.zoomit.ir/android/430775-android-15-qpr1-pixel-december-feature-drop/"]

# # async def analyze_website(url: List[str]):
# async def analyze_websites(urls: List[str]):
#     analyzer = ContentAnalyzer(
#         base_url="https://api.avalai.ir/v1",
#         api_key ="aa-ToRw47f4fT9QPqHEeiFHoPXY6IGudBoYzUnx2iD5DIYLNmaU",
#     )
#     all_report = []
#     for url in urls:
#         print(f"\nAnalyzing {url}...")
#         try:
#             raw_content = await ascrape_playwright(url)

#             with open("extracted_content.txt" , "w" , encoding='utf-8') as f:
#                 f.write(f"\nURL: {url}\n\n")
#                 f.write(raw_content)

#             if raw_content and not raw_content.startswith("Error"):
#                 report =  analyzer.analyze_content(raw_content)

#                 if report:
#                     all_report.append(report)

#                     print("\n" + "="*50)
#                     print(f"Title: {report.title}")
#                     print("-"*50)
#                     print("\nSummary:")
#                     print(report.summary)
#                     print("\nContent:", report.content)   
#                     print("="*50)
#                     print("\nHashtags:" , report.hasgtag)
#                     print("="*50)
#             else:
#                 print("no content extracted")        
#         except Exception as e:
#             print(f"Error:{e}")
#     return all_report        
# if __name__ == "__main__":
#     reports = asyncio.run(analyze_websites(urls))

#     with open("republished_news.txt" , "w" , encoding='utf-8') as f:
#         for report in reports:
            
#                     f.write("\n" + "="*50)
#                     f.write(f"\nTitle: {report.title}")
#                     f.write("\n" + "="*50)
#                     f.write("\nSummary:")
#                     f.write(report.summary)
#                     f.write("\n" + "="*50)
#                     f.write("\nContent:")
#                     f.write(report.content)   
#                     f.write("\n" + "="*50)
#                     f.write("\nHashtags:")
#                     f.write(report.hasgtag)
#                     f.write("\n" + "="*50) 
#     asyncio.run(upload_playwright("https://tejaratnews.com/admin-start-b2dc"))


# -------------------------------------------------------------------------------------------------
import asyncio
from typing import List
from bs4 import BeautifulSoup
from ai_extractor import ContentAnalyzer
from schema import websiteReport
from sctape import ascrape_playwright
from auto_uploader import upload_playwright

async def upload_republish_to_txtfile(reports):
    with open("republished_news.txt", "w", encoding='utf-8') as f:
        for report in reports:
            f.write("\n" + "="*50)
            f.write(f"\nTitle: {report.title}")
            f.write("\n" + "="*50)
            f.write("\nSummary:")
            f.write(report.summary)
            f.write("\n" + "="*50)
            f.write("\nContent:")
            f.write(report.content)   
            f.write("\n" + "="*50)
            f.write("\nHashtags:")
            f.write(report.hasgtag)
            f.write("\n" + "="*50)
    return     

async def analyze_websites(urls: List[str]):
    analyzer = ContentAnalyzer(
        base_url="https://api.avalai.ir/v1",
        api_key="aa-ToRw47f4fT9QPqHEeiFHoPXY6IGudBoYzUnx2iD5DIYLNmaU",
    )
    all_report = []
    for url in urls:
        print(f"\nAnalyzing {url}...")
        try:
            raw_content = await ascrape_playwright(url)

            with open("extracted_content.txt", "w", encoding='utf-8') as f:
                f.write(f"\nURL: {url}\n\n")
                f.write(raw_content)

            if raw_content and not raw_content.startswith("Error"):
                report = analyzer.analyze_content(raw_content)

                if report:
                    all_report.append(report)

                    print("\n" + "="*50)
                    print(f"Title: {report.title}")
                    print("-"*50)
                    print("\nSummary:")
                    print(report.summary)
                    print("\nContent:", report.content)   
                    print("="*50)
                    print("\nHashtags:", report.hasgtag)
                    print("="*50)
            else:
                print("no content extracted")        
        except Exception as e:
            print(f"Error:{e}")
    return all_report        

if __name__ == "__main__":
    # Test URL
    # test_url = "https://www.zoomit.ir/android/430775-android-15-qpr1-pixel-december-feature-drop/"
    
    # Run the analysis
    # reports = asyncio.run(analyze_websites([test_url]))

    # Write reports to file
    with open("republished_news.txt", "w", encoding='utf-8') as f:
        for report in reports:
            f.write("\n" + "="*50)
            f.write(f"\nTitle: {report.title}")
            f.write("\n" + "="*50)
            f.write("\nSummary:")
            f.write(report.summary)
            f.write("\n" + "="*50)
            f.write("\nContent:")
            f.write(report.content)   
            f.write("\n" + "="*50)
            f.write("\nHashtags:")
            f.write(report.hasgtag)
            f.write("\n" + "="*50) 

    # Note: We're removing the direct call to upload_playwright here
    # The upload functionality should be called from the telegram bot
    # with proper credentials      
    