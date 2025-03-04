# import os
# from langchain.chains import create_extraction_chain, create_extraction_chain_pydantic
# from langchain.chat_models import ChatOpenAI
# from pydantic import BaseModel
# from schema import websiteReport

# class ContentAnalyzer:
#     def __init__(self, api_key: str, base_url: str):
#         self.llm = ChatOpenAI(model = "gpt-4o-mini" , base_url = base_url, api_key = api_key)
#     def generator_prompt(self , news_content: str) -> str:
#         return f"""
#             You are tasked with analyzing the text stored in news_content, which contains the full content of a news article. Your objective is to transform this information into a republishable format in Persian while adhering to the following guidelines:

#             Title: Generate a new, engaging, and concise headline for the news article. The title must be clear, attractive, and no longer than 55 characters. It should differ significantly in word choice and structure from the original content.
#             Summary: Provide a complete, informative summary of the article in Persian, covering its key points in a maximum of 155 characters. The summary should offer a quick overview while remaining unique in phrasing from the original.
#             Content: Rewrite the entire news article in Persian into at least 500 words. The rewritten version must differ in vocabulary, structure, and tone while maintaining the original meaning and intent.
#             Tags: Extract 3–4 relevant hashtags in Persian from the rewritten content. The hashtags should reflect key topics or themes of the article and follow the format #Hashtag1 #Hashtag2 #Hashtag3.

#             Content to analyze:
#             {news_content}

#             Output Format:
#             Your response should match the WebsiteReport schema, containing the following fields:

#             title: The new headline (Persian)
#             summary: The informative summary (Persian)
#             content: The rewritten news text (Persian, at least 500 words).
#             hashtag: A string of 3–4 hashtags, formatted as #Hashtag1 #Hashtag2 #Hashtag3.

#             Ensure:
#             - All output elements are written in Persian and significantly differ from the original news_content.
#             - The rewritten content is natural, well-structured, error-free, and coherent.
#             - The response adheres strictly to the schema and guidelines.
#               """
#     def analyze_content(self, content: str) -> websiteReport:
#         prompt = self.generator_prompt(content)
#         analysis_chain = create_extraction_chain_pydantic(
#             pydantic_schema = websiteReport,
#             llm = self.llm
#         )     
#         result = analysis_chain.run(prompt)
#         if result:
            
#             return result[0]
#         return None
    # ---------------------------------------------------------------------------------

# import os
# from langchain.chains import create_extraction_chain
# from langchain.chat_models import ChatOpenAI
# from schema import websiteReport

# class ContentAnalyzer:
#     def __init__(self, api_key: str, base_url: str):
#         try:
#             self.llm = ChatOpenAI(
#                 model="gpt-4o-mini",
#                 base_url=base_url,
#                 api_key=api_key
#             )
#             print("LLM initialized successfully")
#         except Exception as e:
#             print(f"Error initializing LLM: {e}")
#             raise

#     def generator_prompt(self, news_content: str) -> str:
#         return f"""
#             You are tasked with analyzing the text stored in news_content, which contains the full content of a news article. Your objective is to transform this information into a republishable format in Persian while adhering to the following guidelines:

#             Title: Generate a new, engaging, and concise headline for the news article. The title must be clear, attractive, and no longer than 55 characters. It should differ significantly in word choice and structure from the original content.
#             Summary: Provide a complete, informative summary of the article in Persian, covering its key points in a maximum of 155 characters. The summary should offer a quick overview while remaining unique in phrasing from the original.
#             Content: Rewrite the entire news article in Persian into at least 500 words. The rewritten version must differ in vocabulary, structure, and tone while maintaining the original meaning and intent.
#             Tags: Extract 3–4 relevant hashtags in Persian from the rewritten content. The hashtags should reflect key topics or themes of the article and follow the format #Hashtag1 #Hashtag2 #Hashtag3.

#             Content to analyze:
#             {news_content}

#             Output Format:
#             Your response should match the WebsiteReport schema, containing the following fields:

#             title: The new headline (Persian)
#             summary: The informative summary (Persian)
#             content: The rewritten news text (Persian, at least 500 words)
#             hashtag: A string of 3–4 hashtags, formatted as #Hashtag1 #Hashtag2 #Hashtag3
#         """

#     def analyze_content(self, content: str) -> websiteReport:
#         try:
#             print("Starting content analysis...")
#             prompt = self.generator_prompt(content)
#             print("Generated prompt successfully")

#             # Define the schema for extraction
#             schema = {
#                 "properties": {
#                     "title": {"type": "string"},
#                     "summary": {"type": "string"},
#                     "content": {"type": "string"},
#                     "hashtag": {"type": "string"}
#                 },
#                 "required": ["title", "summary", "content", "hashtag"]
#             }

#             # Create and run the extraction chain
#             chain = create_extraction_chain(schema, self.llm)
#             result = chain.run(prompt)
#             print("Obtained analysis result:", result)

#             if result and isinstance(result, list) and len(result) > 0:
#                 # Convert dictionary to websiteReport
#                 report_data = result[0]
#                 return websiteReport(
#                     title=report_data["title"],
#                     summary=report_data["summary"],
#                     content=report_data["content"],
#                     hasgtag=report_data["hashtag"]
#                 )
#             else:
#                 print("Warning: No valid result obtained from analysis chain")
#                 return None
#         except Exception as e:
#             print(f"Error in analyze_content: {e}")
#             raise
# ----------------------------------------------------------------
# import os
# from langchain.chains import create_extraction_chain
# from langchain.chat_models import ChatOpenAI
# from schema import websiteReport
# from langchain.prompts import ChatPromptTemplate

# class ContentAnalyzer:
#     def __init__(self, api_key: str, base_url: str):
#         try:
#             self.llm = ChatOpenAI(
#                 model="gpt-4o-mini",  # Changed from gpt-4o-mini to gpt-4
#                 base_url=base_url,
#                 api_key=api_key,
#                 temperature=0.7
#             )
#             print("LLM initialized successfully")
#         except Exception as e:
#             print(f"Error initializing LLM: {e}")
#             raise

#     def generator_prompt(self, news_content: str) -> str:
#         return f"""تحلیل و بازنویسی متن خبر به فارسی:

# متن اصلی خبر:
# {news_content}

# لطفاً خبر را با رعایت موارد زیر بازنویسی کنید:

# 1. عنوان: یک تیتر جذاب و گیرا (حداکثر 55 کاراکتر)
# 2. خلاصه: خلاصه‌ای از خبر (حداکثر 155 کاراکتر)
# 3. محتوا: متن کامل خبر با مشخصات زیر:
#    - حداقل 700 کلمه
#    - پاراگراف اول به عنوان مقدمه، بدون عنوان باشد
#    - بخش‌های میانی هر کدام دارای:
#      * یک عنوان 
#      * یک پاراگراف مرتبط با آن عنوان
#    - پاراگراف پایانی به عنوان جمع‌بندی، بدون عنوان باشد
#    - هر بخش باید در پاراگراف مجزا قرار گیرد
# 4. هشتگ: 3 تا 4 هشتگ مرتبط با موضوع اصلی خبر

# لطفاً خروجی را دقیقاً در قالب زیر ارائه دهید:
# TITLE: [عنوان]
# SUMMARY: [خلاصه]
# CONTENT: [محتوا با ساختار پاراگراف‌بندی و عناوین مشخص شده]
# HASHTAGS: [هشتگ‌ها]
# """

#     def analyze_content(self, content: str) -> websiteReport:
#         try:
#             print("Starting content analysis...")
#             prompt = self.generator_prompt(content)
#             print("Generated prompt successfully")

#             # Get direct response from LLM
#             response = self.llm.predict(prompt)
#             print("Received LLM response")

#             # Parse the response
#             sections = response.split('\n')
#             title = ""
#             summary = ""
#             content = ""
#             hashtags = ""
#             current_section = None

#             for line in sections:
#                 line = line.strip()
#                 if line.startswith('TITLE:'):
#                     current_section = 'title'
#                     title = line.replace('TITLE:', '').strip()
#                 elif line.startswith('SUMMARY:'):
#                     current_section = 'summary'
#                     summary = line.replace('SUMMARY:', '').strip()
#                 elif line.startswith('CONTENT:'):
#                     current_section = 'content'
#                     content = line.replace('CONTENT:', '').strip()
#                 elif line.startswith('HASHTAGS:'):
#                     current_section = 'hashtags'
#                     hashtags = line.replace('HASHTAGS:', '').strip()
#                 elif line and current_section:
#                     if current_section == 'content':
#                         content += '\n' + line
#                     elif current_section == 'hashtags' and not hashtags:
#                         hashtags = line

#             if title and summary and content and hashtags:
#                 return websiteReport(
#                     title=title,
#                     summary=summary,
#                     content=content,
#                     hasgtag=hashtags
#                 )
#             else:
#                 print("Warning: Missing required fields in LLM response")
#                 print(f"Title: {bool(title)}, Summary: {bool(summary)}, Content: {bool(content)}, Hashtags: {bool(hashtags)}")
#                 return None

#         except Exception as e:
#             print(f"Error in analyze_content: {e}")
#             raise
        # -------------------------------------------------------------
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from schema import websiteReport

class ContentAnalyzer:
    def __init__(self, api_key: str, base_url: str):
        try:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                base_url=base_url,
                api_key=api_key,
                temperature=0.7,
                max_tokens=2000
            )
            print("LLM initialized successfully")
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            raise

    def generator_prompt(self, news_content: str) -> str:
        return f"""تحلیل و بازنویسی متن خبر به فارسی:

متن اصلی خبر:
{news_content}

لطفاً خبر را با رعایت موارد زیر بازنویسی کنید:

1. عنوان: یک تیتر جذاب و گیرا (حداکثر 55 کاراکتر)
2. خلاصه: خلاصه‌ای از خبر (حداکثر 155 کاراکتر)
3. محتوا: متن کامل خبر با مشخصات زیر:
   - حداقل 700 کلمه
   - پاراگراف اول به عنوان مقدمه، بدون عنوان باشد
   - بخش‌های میانی هر کدام دارای:
     *  یک عنوان مشخص بدون علامت (#)
     * یک پاراگراف مرتبط با آن عنوان
   - پاراگراف پایانی به عنوان جمع‌بندی، بدون عنوان باشد
4. هشتگ: 3 تا 4 هشتگ مرتبط با موضوع اصلی خبر

خروجی باید دقیقاً در این قالب باشد:

TITLE:
[عنوان خبر]

SUMMARY:
[خلاصه خبر]

CONTENT:
[متن کامل خبر]

HASHTAGS:
[هشتگ‌ها]"""

    def analyze_content(self, content: str) -> websiteReport:
        try:
            print("Starting content analysis...")
            prompt = self.generator_prompt(content)
            print("Generated prompt successfully")

            # Send message to LLM
            messages = [HumanMessage(content=prompt)]
            response = self.llm.predict_messages(messages).content
            print("Received LLM response")

            # Parse the response
            sections = response.split('\n')
            current_section = None
            data = {
                'title': '',
                'summary': '',
                'content': [],
                'hashtags': ''
            }

            for line in sections:
                line = line.strip()
                if not line:
                    continue

                if 'TITLE:' in line:
                    current_section = 'title'
                    continue
                elif 'SUMMARY:' in line:
                    current_section = 'summary'
                    continue
                elif 'CONTENT:' in line:
                    current_section = 'content'
                    continue
                elif 'HASHTAGS:' in line:
                    current_section = 'hashtags'
                    continue

                if current_section == 'title' and not data['title']:
                    data['title'] = line
                elif current_section == 'summary' and not data['summary']:
                    data['summary'] = line
                elif current_section == 'content':
                    data['content'].append(line)
                elif current_section == 'hashtags' and not data['hashtags']:
                    data['hashtags'] = line

            # Join content with proper line breaks
            full_content = '\n'.join(data['content'])

            # Verify all sections have content
            if all([data['title'], data['summary'], full_content, data['hashtags']]):
                print("Successfully parsed all sections")
                return websiteReport(
                    title=data['title'],
                    summary=data['summary'],
                    content=full_content,
                    hasgtag=data['hashtags']
                )
            else:
                print("Warning: Missing required fields in LLM response")
                print(f"Title present: {bool(data['title'])}")
                print(f"Summary present: {bool(data['summary'])}")
                print(f"Content present: {bool(full_content)}")
                print(f"Hashtags present: {bool(data['hashtags'])}")
                return None

        except Exception as e:
            print(f"Error in analyze_content: {e}")
            raise