
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