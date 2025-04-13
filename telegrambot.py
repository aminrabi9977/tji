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
    SUBSERVICE,
    WAIT_FOR_LINK,
    AFTER_UPLOAD
) = range(7)  # Removed INTERNATIONAL_CHOICE state since we don't need it anymore

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
                await page.goto("https://tejaratnews.com/wp-admin")
                
                await page.wait_for_timeout(300)
                await page.fill('#user_login', context.user_data['username'])
                await page.fill('#user_pass', context.user_data['password'])
                await page.wait_for_timeout(300)
                await page.click('#wp-submit')
                await page.wait_for_timeout(3000)
                
                if "wp-admin" in page.url:
                    await browser.close()
                    await update.message.reply_text("✅ با موفقیت وارد شدید!")
                    # Updated service selection with 4 options
                    keyboard = [
                        [
                            InlineKeyboardButton("علم و فناوری", callback_data="science"),
                            InlineKeyboardButton("ارز دیجیتال", callback_data="crypto")
                        ],
                        [
                            InlineKeyboardButton("سیاسی", callback_data="political"),
                            InlineKeyboardButton("فرهنگی", callback_data="cultural")
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
        "crypto": "ارز دیجیتال",
        "political": "سیاسی",
        "cultural": "فرهنگی"
    }
    
    selected_service = query.data
    context.user_data['service'] = service_map[selected_service]
    context.user_data['service_code'] = selected_service
    
    # If the selected service is "فرهنگی", skip the subservice selection
    if selected_service == "cultural":
        context.user_data['categories'] = ["فرهنگی"]
        await query.message.reply_text("لطفا لینک خبر را وارد کنید:")
        return WAIT_FOR_LINK
    
    # For other services, proceed to sub-service selection
    if selected_service == "science":
        # For "علم و فناوری", show its sub-services
        keyboard = [
            [
                InlineKeyboardButton("هوش مصنوعی", callback_data="ai"),
                InlineKeyboardButton("تکنولوژی", callback_data="tech")
            ],
            [
                InlineKeyboardButton("استارتاپ", callback_data="startup")
            ],
            [
                InlineKeyboardButton("بازگشت", callback_data="back_to_service")
            ]
        ]
        
    elif selected_service == "crypto":
        # For "ارز دیجیتال", show its sub-services
        keyboard = [
            [
                InlineKeyboardButton("تحلیل ارز دیجیتال", callback_data="crypto_analysis"),
                InlineKeyboardButton("آموزش ارز دیجیتال", callback_data="crypto_education")
            ],
            [
                InlineKeyboardButton("اخبار ارز دیجیتال", callback_data="crypto_news")
            ],
            [
                InlineKeyboardButton("بازگشت", callback_data="back_to_service")
            ]
        ]
        
    elif selected_service == "political":
        # For "سیاسی", show its sub-services with combined "دیپلماسی-بین الملل" option
        keyboard = [
            [
                InlineKeyboardButton("دیپلماسی", callback_data="diplomacy"),
                InlineKeyboardButton("دیپلماسی-بین الملل", callback_data="diplomacy_intl")
            ],
            [
                InlineKeyboardButton("سیاست خارجی", callback_data="foreign_policy"),
                InlineKeyboardButton("سیاست داخلی", callback_data="internal_policy")
            ],
            [
                InlineKeyboardButton("مجلس", callback_data="parliament"),
                InlineKeyboardButton("بازگشت", callback_data="back_to_service")
            ]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفا زیر سرویس را انتخاب کن:", reply_markup=reply_markup)
    return SUBSERVICE

async def handle_subservice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sub-service selection."""
    query = update.callback_query
    await query.answer()
    
    # Handle "Back" button
    if query.data == "back_to_service":
        keyboard = [
            [
                InlineKeyboardButton("علم و فناوری", callback_data="science"),
                InlineKeyboardButton("ارز دیجیتال", callback_data="crypto")
            ],
            [
                InlineKeyboardButton("سیاسی", callback_data="political"),
                InlineKeyboardButton("فرهنگی", callback_data="cultural")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "لطفا سرویس را انتخاب کن:",
            reply_markup=reply_markup
        )
        return SERVICE
    
    # Map the callback data to category names
    subservice_map = {
        # علم و فناوری sub-services
        "ai": "هوش مصنوعی",
        "tech": "تکنولوژی",
        "startup": "استارتاپ",
        
        # ارز دیجیتال sub-services
        "crypto_analysis": "تحلیل ارز دیجیتال",
        "crypto_education": "آموزش ارز دیجیتال",
        "crypto_news": "اخبار ارز دیجیتال",
        
        # سیاسی sub-services
        "diplomacy": "دیپلماسی",
        "diplomacy_intl": "دیپلماسی-بین الملل",  # New combined option
        "foreign_policy": "سیاست خارجی",
        "internal_policy": "سیاست داخلی",
        "parliament": "مجلس"
    }
    
    # Store the selected subservice
    selected_subservice = query.data
    context.user_data['subservice'] = selected_subservice
    context.user_data['subservice_name'] = subservice_map.get(selected_subservice, "")
    
    # Set categories based on selection
    service_code = context.user_data.get('service_code')
    
    if service_code == "science":
        context.user_data['categories'] = ["علم و فناوری", subservice_map[selected_subservice]]
    elif service_code == "crypto":
        context.user_data['categories'] = ["ارز دیجیتال", subservice_map[selected_subservice]]
    elif service_code == "political":
        # Special case for diplomacy with international
        if selected_subservice == "diplomacy_intl":
            context.user_data['categories'] = ["سیاسی", "دیپلماسی", "بین الملل"]
        else:
            context.user_data['categories'] = ["سیاسی", subservice_map[selected_subservice]]
    
    await query.message.reply_text("لطفا لینک خبر را وارد کنید:")
    return WAIT_FOR_LINK

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle news link and process it."""
    url = update.message.text
    context.user_data['url'] = url
    context.user_data['original_url'] = url  # Save the original URL for source field
    
    try:
        await update.message.reply_text("📝 در حال پردازش درخواست...")
        await update.message.reply_text("🔍 استخراج خبر از لینک ارسالی ...")
        
        reports = await analyze_websites([url])
        await update.message.reply_text("🔄 در حال تحلیل و بازنشر خبر...")
        await upload_republish_to_txtfile(reports)
        
        await update.message.reply_text("در حال بارگذاری اطلاعات در سایت تجارت نیوز...")
        
        # Get the categories from user data
        categories = context.user_data.get('categories')
        
        # Upload to WordPress - Pass the original URL for the source field
        await upload_playwright(
            url="https://tejaratnews.com/wp-admin",
            select_services=context.user_data['service'],
            username=context.user_data['username'],
            password=context.user_data['password'],
            categories=categories,  # Pass the categories
            original_url=context.user_data['original_url']  # Pass the original URL
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
            ],
            [
                InlineKeyboardButton("سیاسی", callback_data="political"),
                InlineKeyboardButton("فرهنگی", callback_data="cultural")
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
            SUBSERVICE: [CallbackQueryHandler(handle_subservice)],
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