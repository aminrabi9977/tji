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
     * یک عنوان مشخص بدون علامت (#)
     * یک پاراگراف مرتبط با آن عنوان
   - عنوان پاراگراف ها با (##) شروع شود
   - پاراگراف پایانی به عنوان جمع‌بندی، بدون تیتر "جمع بندی" باشد
4. هشتگ: 1 کلمه کلیدی مرتبط با موضوع اصلی خبر (بدون علامت #)
5. کلمه کلیدی SEO: یک کلمه یا عبارت کلیدی اصلی را مشخص کنید که:
   - آن کلمه یا عبارت عیناً در عنوان خبر استفاده شده باشد
   - آن کلمه یا عبارت عیناً در خلاصه مطلب استفاده شده باشد
   - آن کلمه یا عبارت عیناً در ابتدای متن (پاراگراف اول) استفاده شده باشد
   - آمکلمه یا عبارت عیناً در متن اصلی استفاده شده باشد
   - بهترین کلمه کلیدی برای سئو باشد
   - با کلمه کلیدی هشتگ متفاوت باشد
   - کلمه کلیدی اصلی بدون نیم فاصله باشد
خروجی باید دقیقاً در این قالب باشد:

TITLE:
[عنوان خبر]

SUMMARY:
[خلاصه خبر]

CONTENT:
[متن کامل خبر]

HASHTAGS:
[کلمات کلیدی با کاما جدا شده]

SEO_KEYWORD:
[کلمه کلیدی اصلی برای سئو]"""

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
                'hashtags': '',
                'seo_keyword': ''
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
                elif 'SEO_KEYWORD:' in line:
                    current_section = 'seo_keyword'
                    continue

                if current_section == 'title' and not data['title']:
                    data['title'] = line
                elif current_section == 'summary' and not data['summary']:
                    data['summary'] = line
                elif current_section == 'content':
                    data['content'].append(line)
                elif current_section == 'hashtags' and not data['hashtags']:
                    data['hashtags'] = line
                elif current_section == 'seo_keyword' and not data['seo_keyword']:
                    data['seo_keyword'] = line

            # Join content with proper line breaks
            full_content = '\n'.join(data['content'])

            # Verify all sections have content
            if all([data['title'], data['summary'], full_content, data['hashtags'], data['seo_keyword']]):
                print("Successfully parsed all sections")
                return websiteReport(
                    title=data['title'],
                    summary=data['summary'],
                    content=full_content,
                    hasgtag=data['hashtags'],
                    seo_keyword=data['seo_keyword']
                )
            else:
                print("Warning: Missing required fields in LLM response")
                print(f"Title present: {bool(data['title'])}")
                print(f"Summary present: {bool(data['summary'])}")
                print(f"Content present: {bool(full_content)}")
                print(f"Hashtags present: {bool(data['hashtags'])}")
                print(f"SEO keyword present: {bool(data['seo_keyword'])}")
                return None

        except Exception as e:
            print(f"Error in analyze_content: {e}")
            raise