# from playwright.async_api import async_playwright
# import asyncio
# import time
# async def print_dashes(stop_flag):
#     while not stop_flag.is_set():
#         print("-", end="", flush=True)
#         await asyncio.sleep(0.1)
# async def read_republish_news():
#     with open('republished_news.txt' , 'r' , encoding = 'utf-8') as f:
#         news_report = f.read()
#     lines = news_report.strip().split('==================================================')  
#     title = lines[1].split("Title:")[1].strip()  
#     summary = lines[2].split("Summary:")[1].strip()  
#     content = lines[3].split("Content:")[1].strip()  
#     hashtags = lines[4].split("Hashtags:")[1].strip()  
#     return  {
#         'title': title,  
#         'summary': summary,  
#         'content': content,  
#         'hashtags': hashtags  
#     }  
# async def selected_services(select_services):
#     finall_services = []
#     AI_services = ['علم و فناوری', 'تکنولوژی', 'هوش مصنوعی']
#     dig_services = ['ارز دیجیتال' , 'تحلیل ارز دیجیتال' , 'آموزش ارز دیجیتال', 'خبار ارز دیجیتال']
#     # select_services = input("which services: ")
#     if select_services == 'علم و فناوری':
#         finall_services.append(AI_services)
#     elif select_services == 'ارز دیجیتال': 
#         finall_services.append(dig_services)
#     else:
#         return "There isn't your service"
#     return finall_services        



# async def upload_playwright(url, select_services, publish_date, publish_time) -> str:
# # async def upload_playwright(url) -> str:
#     # select_services = input("which services: ")
#     services_list = await selected_services(select_services)
#     # publish_date = input("set date: ")
#     # publish_time = input("set time: ")
#     publish = publish_date + ' ' +  publish_time
#     print(publish)
#     print("upload news into admin page ....")
#     stop_flag = asyncio.Event()

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         try:
#             context = await browser.new_context()  
#             page = await context.new_page() 
#             await page.goto(url)
#             print("logining" , end='' , flush=True)
#             dashes_task = asyncio.create_task(print_dashes(stop_flag))
#             await page.wait_for_timeout(300)
#             await page.fill('input[name="data[name]"]', 'a.rabiee')  # نام کاربری خود را وارد کنید  
#             await page.fill('input[name="data[password]"]', 'nMytkC4umX77')  # رمز عبور خود را وارد کنید  
#             await page.click('button[type="submit"]')
#             flag = 0
#             await page.wait_for_timeout(3000)
#             if "login" not in page.url:  
#                 stop_flag.set()  
#                 await dashes_task  
#                 print("done")
#                 flag = 1
#             else:
#                 raise Exception("Login failed or incorrect page!")
#             if flag:
#                 await page.goto('https://tejaratnews.com/fa/admin/newsstudios/add/')
#                 await page.wait_for_timeout(1000)
#                 # title, summary, content, hashtags = await read_republish_news()
#                 # print(title)
#                 news_data = await read_republish_news()
#                 await page.fill("input[name='data[Newsstudio][newsstudio_data][upTitle]']", "تجارت‌نیوز گزارش می‌دهد:")
#                 await page.fill('textarea[name="data[Newsstudio][title]"]', news_data['title'])
#                 await page.fill('textarea[name="data[Newsstudio][newsstudio_data][lead]"]', news_data['summary'])
#                 await page.wait_for_selector("#cke_NewsstudioContentContent iframe")
#                 editor_frame = page.frame_locator("#cke_NewsstudioContentContent iframe")
#                 await editor_frame.locator("body").evaluate("element => element.innerHTML = ''")
#                 await editor_frame.locator("body").type(news_data['content'])
#                 print(services_list)
#                 for service in services_list[0]:
#                     await page.fill("#s2id_autogen13", service)
#                     await page.keyboard.press("Enter")
#                     await page.wait_for_timeout(100)
#                 await page.wait_for_timeout(3000)    
#                 await page.select_option("#NewsstudioPositionFront", "2")  
#                 await page.select_option("select[name='data[Newsstudio][order][front][position]']", "1")
#                 position_selectors = await page.query_selector_all(".position-category")
#                 order_selectors = await page.query_selector_all("[data-category-order]")
                
#                 for pos_selector, ord_selector in  zip(position_selectors, order_selectors):
#                    await pos_selector.select_option("2")  
#                    await ord_selector.select_option("1")  
#                 await page.wait_for_timeout(1000)

#                 await page.fill('#s2id_autogen16' , 'گوگل')
#                 await page.wait_for_timeout(100)
#                 await page.keyboard.press("Enter")
#                 await page.wait_for_timeout(1000)
#                 # await page.fill('#s2id_autogen16' , 'اپل')
#                 await page.keyboard.press("Enter")
#                 # await page.click('a[data-original-title="افزودن مؤلفان"]')
#                 await page.wait_for_timeout(1000)
#                 # await page.fill("#s2id_autogen3", "امین ربیعی")
#                 # await page.keyboard.press("Enter")
#                 await page.wait_for_timeout(1000)
#                 # await page.click('div.modal-footer button')
#                 await page.wait_for_timeout(3000)
#                 await page.fill('#NewsstudioPublishTime', publish)
#                 await page.wait_for_timeout(1000)
#                 await page.keyboard.press("Enter")
#                 await page.wait_for_timeout(3000)
#                 await page.click('button[name = "submit"]')
#                 await page.wait_for_timeout(3000)
#             print("sucsee")
#         except Exception as e:
#             stop_flag.set() 
#             await dashes_task  
#             print(f"\nerror: {e}")
#         finally:
#             await browser.close()
#         return None          

# # if __name__ == "__main__":
# #     asyncio.run(upload_playwright("https://tejaratnews.com/admin-start-b2dc"))

# ----------------------------------------------
from playwright.async_api import async_playwright
import asyncio
import time

async def print_dashes(stop_flag):
    while not stop_flag.is_set():
        print("-", end="", flush=True)
        await asyncio.sleep(0.1)

async def read_republish_news():
    with open('republished_news.txt', 'r', encoding='utf-8') as f:
        news_report = f.read()
    lines = news_report.strip().split('==================================================')
    title = lines[1].split("Title:")[1].strip()
    summary = lines[2].split("Summary:")[1].strip()
    content = lines[3].split("Content:")[1].strip()
    hashtags = lines[4].split("Hashtags:")[1].strip()
    return {
        'title': title,
        'summary': summary,
        'content': content,
        'hashtags': hashtags
    }

async def selected_services(select_services):
    finall_services = []
    AI_services = ['علم و فناوری', 'تکنولوژی', 'هوش مصنوعی']
    dig_services = ['ارز دیجیتال', 'تحلیل ارز دیجیتال', 'آموزش ارز دیجیتال', 'اخبار ارز دیجیتال']
    
    if select_services == 'علم و فناوری':
        finall_services.append(AI_services)
    elif select_services == 'ارز دیجیتال':
        finall_services.append(dig_services)
    else:
        return "There isn't your service"
    return finall_services

async def upload_playwright(url, select_services, username, password, publish_date=None, publish_time=None) -> str:
    services_list = await selected_services(select_services)
    
    # Only create publish string if both date and time are provided
    publish = f"{publish_date} {publish_time}" if publish_date and publish_time else None
    
    print("upload news into admin page ....")
    stop_flag = asyncio.Event()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        try:
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url)
            print("logining", end='', flush=True)
            dashes_task = asyncio.create_task(print_dashes(stop_flag))
            await page.wait_for_timeout(300)
            await page.fill('input[name="data[name]"]', username)
            await page.fill('input[name="data[password]"]', password)
            await page.click('button[type="submit"]')
            flag = 0
            await page.wait_for_timeout(3000)
            
            if "login" not in page.url:
                stop_flag.set()
                await dashes_task
                print("done")
                flag = 1
            else:
                raise Exception("Login failed or incorrect page!")
                
            if flag:
                await page.goto('https://tejaratnews.com/fa/admin/newsstudios/add/')
                await page.wait_for_timeout(1000)
                
                news_data = await read_republish_news()
                await page.fill("input[name='data[Newsstudio][newsstudio_data][upTitle]']", "تجارت‌نیوز گزارش می‌دهد:")
                await page.fill('textarea[name="data[Newsstudio][title]"]', news_data['title'])
                await page.fill('textarea[name="data[Newsstudio][newsstudio_data][lead]"]', news_data['summary'])
                
                await page.wait_for_selector("#cke_NewsstudioContentContent iframe")
                editor_frame = page.frame_locator("#cke_NewsstudioContentContent iframe")
                await editor_frame.locator("body").evaluate("element => element.innerHTML = ''")
                await editor_frame.locator("body").type(news_data['content'])
                
                print(services_list)
                for service in services_list[0]:
                    await page.fill("#s2id_autogen13", service)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(100)
                    
                await page.wait_for_timeout(3000)
                await page.select_option("#NewsstudioPositionFront", "2")
                await page.select_option("select[name='data[Newsstudio][order][front][position]']", "1")
                
                position_selectors = await page.query_selector_all(".position-category")
                order_selectors = await page.query_selector_all("[data-category-order]")
                
                for pos_selector, ord_selector in zip(position_selectors, order_selectors):
                    await pos_selector.select_option("2")
                    await ord_selector.select_option("1")
                    
                await page.wait_for_timeout(1000)
                await page.fill('#s2id_autogen16', 'گوگل')
                await page.wait_for_timeout(100)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(1000)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(1000)
                await page.wait_for_timeout(3000)
                
                # Only set publish time if provided
                if publish:
                    await page.fill('#NewsstudioPublishTime', publish)
                    await page.wait_for_timeout(1000)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(3000)
                
                await page.click('button[name="submit"]')
                await page.wait_for_timeout(3000)
                
            print("success")
        except Exception as e:
            stop_flag.set()
            await dashes_task
            print(f"\nerror: {e}")
            raise e
        finally:
            await browser.close()
        return None

#  if __name__ == "__main__":
    #  asyncio.run(upload_playwright("https://tejaratnews.com/admin-pystart-b2dc"))