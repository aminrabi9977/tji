# import asyncio
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
# from main2 import analyze_websites
# from auto_uploader import upload_playwright
# from main2 import upload_republish_to_txtfile
# # States for conversation
# LINK, SERVICE, DATE, TIME = range(4)

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         """👋 سلام!
#         لینک خبری که برای بازنشر میخواهی را به من ارسال کن"""
#     )
#     return LINK

# async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     url = update.message.text
#     context.user_data['url'] = url
    
#     keyboard = [
#         [
#             InlineKeyboardButton("علم و فناوری", callback_data="علم و فناوری"),
#             InlineKeyboardButton("ارز دیجیتال", callback_data="ارز دیجیتال")
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
    
#     await update.message.reply_text(
#         "لطفا سرویس را انتخاب کن:",
#         reply_markup=reply_markup
#     )
#     return SERVICE

# async def handle_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     context.user_data['service'] = query.data
    
#     await query.message.reply_text("لطفا تاریخ انشتار خبر را وارد کنید (برای مثال: 1403/05/12):")
#     return DATE

# async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     context.user_data['date'] = update.message.text
#     await update.message.reply_text("لطفا زمان انتشار را وارد کنید (برای مثال: 10:15:00):")
#     return TIME

# async def handle_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     context.user_data['time'] = update.message.text
#     await update.message.reply_text("📝 در حال پردازش درخواست...")
    
#     # Process the gathered data
#     try:
#         url = context.user_data['url']
#         await update.message.reply_text("🔍 استخراج خبر از لینک ارسالی ...")
#         reports = await analyze_websites([url])
#         await upload_republish_to_txtfile(reports)
        
#         await update.message.reply_text("🔄 در حال بازنشر خبر ...")
#         await upload_playwright(
#             "https://tejaratnews.com/admin-start-b2dc",
#             context.user_data['service'],
#             context.user_data['date'],
#             context.user_data['time']
#         )
        
#         await update.message.reply_text("✅ خبر با موفقیت در تجارت نیوز بارگذاری شد!")
#     except Exception as e:
#         await update.message.reply_text(f"❌ عملیات ناموفق بود: {str(e)}")
    
#     return ConversationHandler.END

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Operation cancelled. Send /start to begin again.")
#     return ConversationHandler.END

# def main():
#     application = Application.builder().token("7581910191:AAE5DR4T9EtC2rTko0_20JJnPaFko51UT-M").build()
    
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler("start", start)],
#         states={
#             LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)],
#             SERVICE: [CallbackQueryHandler(handle_service)],
#             DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)],
#             TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_time)],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)]
#     )
    
#     application.add_handler(conv_handler)
#     application.run_polling()

# if __name__ == "__main__":
#     main()
# -----------------------------------------------------------
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
import asyncio
from playwright.async_api import async_playwright
from main2 import analyze_websites, upload_republish_to_txtfile
from auto_uploader import upload_playwright
import re
import os

# Define states
(
    USERNAME,
    PASSWORD,
    AUTH,
    SERVICE,
    PUBLISH_TIME_CHOICE,
    PUBLISH_DATE,
    PUBLISH_TIME,
    WAIT_FOR_LINK,
    AFTER_UPLOAD
) = range(9)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation."""
    await update.message.reply_text("سلام! به ربات تلگرامی تجارت نیوز خوش آمدید.")
    await update.message.reply_text("برای تولید بازنشر خبر ابتدا باید عملیات احراز هویت را انجام دهی.")
    await update.message.reply_text("نام کاربری را وارد کنید:")
    return USERNAME

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle username input."""
    context.user_data['username'] = update.message.text
    await update.message.reply_text("رمز عبور را وارد کنید:")
    return PASSWORD

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle password input and authenticate."""
    context.user_data['password'] = update.message.text
    await update.message.reply_text("🔄 در حال اعتبارسنجی هویت...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            try:
                context_browser = await browser.new_context()
                page = await context_browser.new_page()
                await page.goto("https://tejaratnews.com/admin-start-b2dc")
                
                await page.wait_for_timeout(300)
                await page.fill('input[name="data[name]"]', context.user_data['username'])
                await page.fill('input[name="data[password]"]', context.user_data['password'])
                await page.wait_for_timeout(300)
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(1000)
                
                if "login" not in page.url:
                    await browser.close()
                    await update.message.reply_text("✅ با موفقیت وارد شدید!")
                    keyboard = [
                        [
                            InlineKeyboardButton("علم و فناوری", callback_data="science"),
                            InlineKeyboardButton("ارز دیجیتال", callback_data="crypto")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        "لطفا سرویس را انتخاب کن:",
                        reply_markup=reply_markup
                    )
                    return SERVICE
                else:
                    await browser.close()
                    await update.message.reply_text("❌ نام کاربری یا رمز عبور اشتباه است!")
                    await update.message.reply_text("نام کاربری را وارد کنید:")
                    return USERNAME
                    
            except Exception as e:
                await browser.close()
                await update.message.reply_text(f"Error during authentication: {str(e)}")
                await update.message.reply_text("نام کاربری را وارد کنید:")
                return USERNAME
                
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
        await update.message.reply_text("نام کاربری را وارد کنید:")
        return USERNAME

async def handle_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service selection."""
    query = update.callback_query
    await query.answer()
    
    service_map = {
        "science": "علم و فناوری",
        "crypto": "ارز دیجیتال"
    }
    
    context.user_data['service'] = service_map[query.data]
    
    keyboard = [
        [
            InlineKeyboardButton("اکنون", callback_data="now"),
            InlineKeyboardButton("تاریخ انتخابی", callback_data="custom")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "زمان انتشار",
        reply_markup=reply_markup
    )
    return PUBLISH_TIME_CHOICE

async def handle_publish_time_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle publish time choice."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "now":
        context.user_data['publish_now'] = True
        await query.message.reply_text("لطفا لینک خبر را وارد کنید:")
        return WAIT_FOR_LINK
    else:
        context.user_data['publish_now'] = False
        await query.message.reply_text("تاریخ انشار را وارد کنید (به فرمت 1402/02/03):")
        return PUBLISH_DATE

async def handle_publish_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle publish date input."""
    date_text = update.message.text
    date_pattern = r'^\d{4}/\d{2}/\d{2}$'
    
    if not re.match(date_pattern, date_text):
        await update.message.reply_text("فرمت تاریخ درست نیست و مجددا وارد کنید:")
        return PUBLISH_DATE
    
    context.user_data['date'] = date_text
    await update.message.reply_text("زمان انتشار را وارد کنید (به فرمت 12:05:00):")
    return PUBLISH_TIME

async def handle_publish_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle publish time input."""
    time_text = update.message.text
    time_pattern = r'^\d{2}:\d{2}:\d{2}$'
    
    if not re.match(time_pattern, time_text):
        await update.message.reply_text("فرمت زمان درست نیست و مجددا وارد کنید:")
        return PUBLISH_TIME
    
    context.user_data['time'] = time_text
    await update.message.reply_text("لطفا لینک خبر را وارد کنید:")
    return WAIT_FOR_LINK

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle news link and process it."""
    url = update.message.text
    context.user_data['url'] = url
    
    try:
        await update.message.reply_text("📝 در حال پردازش درخواست...")
        await update.message.reply_text("🔍 استخراج خبر از لینک ارسالی ...")
        
        reports = await analyze_websites([url])
        await update.message.reply_text("🔄 در حال بازنشر خبر...")
        await upload_republish_to_txtfile(reports)
        
        await update.message.reply_text("در حال بارگذاری اطلاعات در سایت تجارت نیوز...")
        
        # Upload based on publish time choice
        if context.user_data.get('publish_now', False):
            await upload_playwright(
                url="https://tejaratnews.com/admin-start-b2dc",
                select_services=context.user_data['service'],
                username=context.user_data['username'],
                password=context.user_data['password']
            )
        else:
            await upload_playwright(
                url="https://tejaratnews.com/admin-start-b2dc",
                select_services=context.user_data['service'],
                username=context.user_data['username'],
                password=context.user_data['password'],
                publish_date=context.user_data['date'],
                publish_time=context.user_data['time']
            )
        
        # Clear temporary files
        open('extracted_content.txt', 'w', encoding='utf-8').close()
        open('republished_news.txt', 'w', encoding='utf-8').close()
        
        await update.message.reply_text("✅ خبر با موفقیت در تجارت نیوز بارگذاری شد!")
        
        # Provide next action options
        keyboard = [
            [
                InlineKeyboardButton("بازنشر خبری دیگر", callback_data="another_news"),
                InlineKeyboardButton("خروج از حساب", callback_data="logout")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "چه کاری می‌خواهید انجام دهید؟",
            reply_markup=reply_markup
        )
        return AFTER_UPLOAD
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در پردازش خبر: {str(e)}")
        return ConversationHandler.END

async def handle_after_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user choice after successful upload."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "another_news":
        keyboard = [
            [
                InlineKeyboardButton("علم و فناوری", callback_data="science"),
                InlineKeyboardButton("ارز دیجیتال", callback_data="crypto")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "لطفا سرویس را انتخاب کن:",
            reply_markup=reply_markup
        )
        return SERVICE
    else:  # logout
        await query.message.reply_text("شما از صفحه ادمین خارج شدید")
        keyboard = [[InlineKeyboardButton("ورود", callback_data="login")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("برای ورود مجدد کلیک کنید:", reply_markup=reply_markup)
        return ConversationHandler.END

async def handle_login_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle login button press after logout."""
    query = update.callback_query
    await query.answer()
    
    # Clear any existing user data
    context.user_data.clear()
    
    await query.message.reply_text("برای تولید بازنشر خبر ابتدا باید عملیات احراز هویت را انجام دهی.")
    await query.message.reply_text("نام کاربری را وارد کنید:")
    return USERNAME

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text("عملیات لغو شد. برای شروع مجدد /start را بزنید.")
    return ConversationHandler.END

def main():
    """Start the bot."""
    application = Application.builder().token("7581910191:AAE5DR4T9EtC2rTko0_20JJnPaFko51UT-M").build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(handle_login_button, pattern="^login$")
        ],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
            SERVICE: [CallbackQueryHandler(handle_service)],
            PUBLISH_TIME_CHOICE: [CallbackQueryHandler(handle_publish_time_choice)],
            PUBLISH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_publish_date)],
            PUBLISH_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_publish_time)],
            WAIT_FOR_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)],
            AFTER_UPLOAD: [CallbackQueryHandler(handle_after_upload)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
# ----------------------------------------------------------------
