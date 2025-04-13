from playwright.async_api import async_playwright
import asyncio
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def print_progress(message, duration=2):
    """Display progress with animated dots."""
    print(f"{message}", end="", flush=True)
    for _ in range(10):
        print(".", end="", flush=True)
        await asyncio.sleep(duration/10)
    print(" ✓")

async def read_republish_news():
    """Read and parse news content from the file."""
    try:
        with open('republished_news.txt', 'r', encoding='utf-8') as f:
            news_report = f.read()
        
        lines = news_report.strip().split('==================================================')
        title = lines[1].split("Title:")[1].strip() if len(lines) > 1 else ""
        summary = lines[2].split("Summary:")[1].strip() if len(lines) > 2 else ""
        content = lines[3].split("Content:")[1].strip() if len(lines) > 3 else ""
        hashtags = lines[4].split("Hashtags:")[1].strip() if len(lines) > 4 else ""
        seo_keyword = lines[5].split("SEO_KEYWORD:")[1].strip() if len(lines) > 5 else ""
        
        return {
            'title': title,
            'summary': summary,
            'content': content,
            'hashtags': hashtags,
            'seo_keyword': seo_keyword
        }
    except Exception as e:
        logger.error(f"Error reading news file: {e}")
        raise

# New function to get category IDs based on provided category names
async def get_category_ids(categories):
    """
    Convert category names to their corresponding IDs
    
    Parameters:
    - categories: List of category names
    
    Returns:
    - List of category IDs
    """
    # Map of category names to their IDs
    category_id_map = {
        # Main categories
        "علم و فناوری": "54733",
        "ارز دیجیتال": "54338",
        "سیاسی": "54731",
        "فرهنگی": "54730",
        
        # Science and Technology subcategories
        "هوش مصنوعی": "54734",
        "تکنولوژی": "53823",
        "استارتاپ": "54337",
        
        # Cryptocurrency subcategories
        "تحلیل ارز دیجیتال": "54343",
        "آموزش ارز دیجیتال": "54342",
        "اخبار ارز دیجیتال": "54341",
        
        # Political subcategories
        "دیپلماسی": "52249",
        "سیاست خارجی": "54362",
        "سیاست داخلی": "54361",
        "مجلس": "54732",
        "بین الملل": "22"
    }
    
    category_ids = []
    for category in categories:
        if category in category_id_map:
            category_ids.append(category_id_map[category])
    
    return category_ids

async def upload_playwright(url, select_services, username, password, categories=None, publish_date=None, publish_time=None, original_url=None) -> str:
    """Upload news to WordPress with sequential steps and proper delays."""
    logger.info("Starting WordPress upload process")
    
    # Define default category mappings based on service
    service_categories_map = {
        'علم و فناوری': ['علم و فناوری', 'هوش مصنوعی'],
        'ارز دیجیتال': ['ارز دیجیتال', 'اخبار ارز دیجیتال'],
        'سیاسی': ['سیاسی'],
        'فرهنگی': ['فرهنگی']
    }
    
    # Get categories for the selected service - either use provided categories or default ones
    if categories is None:
        categories = service_categories_map.get(select_services, [])
    
    # Convert category names to IDs
    category_ids = await get_category_ids(categories)
    logger.info(f"Using categories: {categories}")
    logger.info(f"Category IDs to select: {category_ids}")
    
    # Create publish string if date and time provided
    publish_string = None
    if publish_date and publish_time:
        publish_string = f"{publish_date} {publish_time}"
        logger.info(f"Scheduled publish time: {publish_string}")
    
    async with async_playwright() as p:
        # Use slower navigation timeouts and longer default timeout
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            accept_downloads=True
        )
        
        # Set default timeout to 60 seconds for all operations
        context.set_default_timeout(60000)
        page = await context.new_page()
        
        try:
            # STEP 1: Navigate to login page
            await print_progress("Navigating to login page")
            await page.goto("https://tejaratnews.com/wp-login.php", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # STEP 2: Login to WordPress
            await print_progress("Logging in to WordPress")
            await page.fill('#user_login', username)
            await asyncio.sleep(1)
            await page.fill('#user_pass', password)
            await asyncio.sleep(1)
            await page.click('#wp-submit')
            
            # Wait for login to complete
            await page.wait_for_url("**/wp-admin/**", timeout=30000)
            logger.info("Login successful")
            await asyncio.sleep(3)
            
            # STEP 3: Navigate to new post page
            await print_progress("Navigating to new post page")
            await page.goto('https://tejaratnews.com/wp-admin/post-new.php', wait_until="domcontentloaded")
            await asyncio.sleep(5)  # Wait for page to fully load
            
            # If direct navigation doesn't work, try clicking menu items
            if not page.url.endswith('post-new.php'):
                logger.info("Direct navigation failed, trying menu navigation")
                try:
                    await page.click('#menu-posts')
                    await asyncio.sleep(2)
                    await page.click('a[href="post-new.php"]')
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.warning(f"Menu navigation error: {e}")
                    # Final attempt with direct navigation
                    await page.goto('https://tejaratnews.com/wp-admin/post-new.php')
                    await asyncio.sleep(5)
            
            # STEP 4: Read the news content
            await print_progress("Reading news content")
            news_data = await read_republish_news()
            await asyncio.sleep(1)
            
            # STEP 5: Fill in title
            await print_progress("Adding title")
            await page.fill('#title', news_data['title'])
            await asyncio.sleep(2)
            
            # STEP 6: Fill in pre-title (روتیتر)
            await print_progress("Adding pre-title")
            await page.fill('#rotitr_ak', '«تجارت‌نیوز» گزارش می‌دهد:')
            await asyncio.sleep(2)
            
            # STEP 7: Fill in the content with retries - USING TYPE METHOD FOR PROPER FORMATTING
            await print_progress("Adding content to editor", duration=5)
            
            success = False
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Content editor attempt {attempt+1}/{max_attempts}")
                    
                    # First check if the TinyMCE editor is loaded
                    is_editor_loaded = await page.evaluate('''
                        typeof tinyMCE !== 'undefined' && tinyMCE.get('content') !== null
                    ''')
                    
                    if not is_editor_loaded:
                        logger.info("Waiting for TinyMCE editor to load...")
                        await asyncio.sleep(5)
                    
                    # Make sure visual tab is active
                    visual_tab = page.locator('#content-tmce')
                    if await visual_tab.is_visible():
                        await visual_tab.click()
                        await asyncio.sleep(3)
                    
                    # Wait for iframe to be available
                    await page.wait_for_selector('#content_ifr', state='visible', timeout=30000)
                    await asyncio.sleep(2)
                    
                    # Access the editor's iframe
                    frame = page.frame_locator('#content_ifr')
                    body = frame.locator('body')
                    
                    # Make sure we can interact with the body
                    await body.wait_for(state='visible', timeout=15000)
                    await body.click()
                    await asyncio.sleep(1)
                    
                    # Clear existing content
                    await page.keyboard.press("Control+a")
                    await asyncio.sleep(0.5)
                    await page.keyboard.press("Delete")
                    await asyncio.sleep(1)
                    
                    # Add content using type method (slower but preserves formatting)
                    # Split content into smaller chunks for more reliable typing
                    logger.info("Starting content typing with slow method for proper heading formatting")
                    content_chunks = [news_data['content'][i:i+500] for i in range(0, len(news_data['content']), 500)]
                    
                    for i, chunk in enumerate(content_chunks):
                        logger.info(f"Typing content chunk {i+1}/{len(content_chunks)}")
                        # Use the type method which preserves special characters like ##
                        await body.type(chunk, delay=5)  # Slower typing speed for reliability
                        await asyncio.sleep(1)
                    
                    success = True
                    break
                    
                except Exception as e:
                    logger.warning(f"Visual editor typing approach failed: {e}")
                    await asyncio.sleep(3)
                    
                    # Try HTML editor approach as fallback
                    try:
                        html_tab = page.locator('#content-html')
                        if await html_tab.is_visible():
                            await html_tab.click()
                            await asyncio.sleep(2)
                            
                            html_textarea = page.locator('#content')
                            await html_textarea.fill(news_data['content'])
                            await asyncio.sleep(2)
                            
                            # Switch back to visual to apply formatting
                            await page.locator('#content-tmce').click()
                            await asyncio.sleep(3)
                            
                            success = True
                            break
                    except Exception as e2:
                        logger.warning(f"HTML editor approach failed: {e2}")
                        await asyncio.sleep(5)  # Longer wait before retry
            
            if not success:
                logger.error("Failed to add content after multiple attempts")
                raise Exception("Content editor interaction failed")
            
            # STEP 8: Fill in summary/excerpt
            await print_progress("Adding summary")
            await page.fill('#excerpt', news_data['summary'])
            await asyncio.sleep(2)
            
            # STEP 9: Select "بازنشر" content type
            await print_progress("Setting content type to 'بازنشر'")
            try:
                # Ensure metabox is expanded
                metabox = page.locator('#metabox_article_type')
                if await metabox.is_visible():
                    # Check if it's collapsed
                    if not await page.locator('#baznashr_ak').is_visible():
                        toggle = page.locator('#metabox_article_type .handlediv')
                        await toggle.click()
                        await asyncio.sleep(2)
                    
                    # Click the radio button for "بازنشر"
                    await page.locator('#baznashr_ak').check()
                    await asyncio.sleep(2)
                    
                    # Fill in source URL if provided
                    if original_url:
                        logger.info(f"Adding source URL: {original_url}")
                        
                        # Wait for source field to appear
                        await asyncio.sleep(2)
                        
                        # Try direct approach first
                        try:
                            await page.evaluate("""
                                // Make sure the source selector is visible
                                if (document.getElementById('source_selector')) {
                                    document.getElementById('source_selector').style.display = 'block';
                                }
                                
                                // Set the value of the custom source field
                                if (document.getElementById('article_custom_source')) {
                                    document.getElementById('article_custom_source').value = arguments[0];
                                }
                            """, original_url)
                            await asyncio.sleep(2)
                        except Exception as e:
                            logger.warning(f"JavaScript approach for source URL failed: {e}")
                        
                        # Try direct input as backup
                        try:
                            await page.fill('#article_custom_source', original_url)
                            await asyncio.sleep(1)
                        except Exception as e:
                            logger.warning(f"Direct fill for source URL failed: {e}")
            except Exception as e:
                logger.warning(f"Error selecting 'بازنشر' or filling source: {e}")
            
            # STEP 10: Select categories - MODIFIED PART
            await print_progress("Setting categories")
            try:
                # Make sure the categories section is visible
                categories_box = page.locator('#categorydiv')
                if not await categories_box.is_visible():
                    toggle_button = page.locator('#categorydiv .handlediv')
                    if await toggle_button.is_visible():
                        await toggle_button.click()
                        await asyncio.sleep(2)
                
                # Make sure we're in the "All Categories" tab
                await page.click('a[href="#category-all"]')
                await asyncio.sleep(2)
                
                # Log the categories we're trying to select
                logger.info(f"Attempting to select categories: {categories}")
                logger.info(f"Using category IDs: {category_ids}")
                
                # Special case for "بین الملل" selection when both "سیاسی" and "دیپلماسی" are selected
                if "22" in category_ids and "52249" in category_ids and "54731" in category_ids:
                    logger.info("Special case: International Relations with Diplomacy and Politics")
                    
                    # First select the political category (parent)
                    political_checkbox = page.locator('#in-category-54731')
                    if await political_checkbox.count() > 0:
                        await political_checkbox.check()
                        logger.info("Selected political category")
                        await asyncio.sleep(1)
                    
                    # Then select the diplomacy category (child of political)
                    diplomacy_checkbox = page.locator('#in-category-52249')
                    if await diplomacy_checkbox.count() > 0:
                        await diplomacy_checkbox.check()
                        logger.info("Selected diplomacy category")
                        await asyncio.sleep(1)
                    
                    # Finally try to select international relations (child of diplomacy)
                    # Try various approaches
                    logger.info("Attempting to select international relations")
                    
                    # First approach: Direct checkbox selection
                    international_checkbox = page.locator('#in-category-22')
                    if await international_checkbox.count() > 0:
                        await international_checkbox.check()
                        logger.info("Selected international relations via direct checkbox")
                        await asyncio.sleep(1)
                    else:
                        # Second approach: Try to find and expand the diplomatic category first
                        try:
                            # Try to expand the parent categories first to make sure all checkboxes are visible
                            await page.evaluate("""
                                // Expand all categories to make sure children are visible
                                document.querySelectorAll('li.expandable').forEach(function(item) {
                                    item.classList.add('expanded');
                                });
                                
                                // Make sure the parent categories are expanded
                                var politicalLi = document.querySelector('li:has(#in-category-54731), li:has(input[value="54731"])');
                                if (politicalLi) {
                                    politicalLi.classList.add('expanded');
                                    
                                    // Find the diplomacy item inside political
                                    var diplomacyLi = politicalLi.querySelector('li:has(#in-category-52249), li:has(input[value="52249"])');
                                    if (diplomacyLi) {
                                        diplomacyLi.classList.add('expanded');
                                    }
                                }
                            """)
                            await asyncio.sleep(1)
                            
                            # Try again after expansion
                            intl_selectors = [
                                '#in-category-22',
                                '#in-category-22-1',
                                '#in-category-22-2',
                                'input[value="22"]',
                                'input[name="post_category[]"][value="22"]'
                            ]
                            
                            for selector in intl_selectors:
                                try:
                                    checkbox = page.locator(selector)
                                    if await checkbox.count() > 0:
                                        await checkbox.check()
                                        logger.info(f"Selected international relations via selector: {selector}")
                                        await asyncio.sleep(1)
                                        break
                                except Exception as e:
                                    logger.warning(f"Error with selector {selector}: {str(e)}")
                            
                            # Third approach: Direct JavaScript approach
                            await page.evaluate("""
                                var found = false;
                                
                                // Try direct checkbox
                                var intlCheck = document.querySelector('#in-category-22, input[value="22"]');
                                if (intlCheck) {
                                    intlCheck.checked = true;
                                    found = true;
                                    console.log("Selected international via JS direct checkbox");
                                }
                                
                                // If not found by ID, try by label text
                                if (!found) {
                                    var labels = document.querySelectorAll('label');
                                    for (var i = 0; i < labels.length; i++) {
                                        if (labels[i].textContent.includes('بین الملل')) {
                                            var input = labels[i].querySelector('input');
                                            if (input) {
                                                input.checked = true;
                                                found = true;
                                                console.log("Selected international via label text");
                                                break;
                                            }
                                        }
                                    }
                                }
                            """)
                            await asyncio.sleep(1)
                            
                        except Exception as e:
                            logger.warning(f"Error expanding categories for international selection: {e}")
                            
                            # Last resort approach: scan all checkboxes
                            try:
                                await page.evaluate("""
                                    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                                    for (var i = 0; i < checkboxes.length; i++) {
                                        var cb = checkboxes[i];
                                        if (cb.value === "22" || 
                                            cb.id === "in-category-22" || 
                                            cb.id === "in-category-22-1" || 
                                            cb.id === "in-category-22-2") {
                                            cb.checked = true;
                                            console.log("Selected international via checkbox scan");
                                            break;
                                        }
                                    }
                                """)
                                await asyncio.sleep(1)
                            except Exception as e2:
                                logger.warning(f"Error in last resort checkbox scan: {e2}")
                else:
                    # Normal category selection
                    for cat_id in category_ids:
                        try:
                            logger.info(f"Looking for category ID: {cat_id}")
                            
                            # Try different selectors for the checkbox
                            selectors = [
                                f'input[type="checkbox"][value="{cat_id}"]',
                                f'#in-category-{cat_id}',
                                f'#in-category-{cat_id}-1',
                                f'#in-category-{cat_id}-2'
                            ]
                            
                            found = False
                            for selector in selectors:
                                checkbox = page.locator(selector)
                                if await checkbox.count() > 0:
                                    logger.info(f"Found checkbox with selector: {selector}")
                                    # Check if it's already checked
                                    is_checked = await checkbox.is_checked()
                                    if not is_checked:
                                        await checkbox.check()
                                        logger.info(f"Checked category with ID {cat_id}")
                                    else:
                                        logger.info(f"Category {cat_id} was already checked")
                                    found = True
                                    await asyncio.sleep(1)
                                    break
                            
                            # If not found by any selector, try JavaScript approach
                            if not found:
                                logger.info(f"Trying JavaScript approach for category {cat_id}")
                                await page.evaluate(f"""
                                    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                                    for (var i = 0; i < checkboxes.length; i++) {{
                                        if (checkboxes[i].value === "{cat_id}" || 
                                            checkboxes[i].id === "in-category-{cat_id}" || 
                                            checkboxes[i].id === "in-category-{cat_id}-1" || 
                                            checkboxes[i].id === "in-category-{cat_id}-2") {{
                                            if (!checkboxes[i].checked) {{
                                                checkboxes[i].checked = true;
                                                console.log("Checked category via JS: {cat_id}");
                                            }}
                                            break;
                                        }}
                                    }}
                                """)
                                await asyncio.sleep(1)
                        except Exception as e:
                            logger.warning(f"Error checking category {cat_id}: {e}")
            except Exception as e:
                logger.warning(f"Error handling categories: {e}")
            
            # STEP 11: Handle the "چینش اخبار" (News Sorting) section
            await print_progress("Setting news sorting options")
            try:
                # Make sure the metabox is expanded
                news_sorting_box = page.locator('#titr_naab_meta')
                if await news_sorting_box.is_visible():
                    # Check if it's collapsed
                    news_sorting_toggle = page.locator('#titr_naab_meta .handlediv')
                    if not await page.locator('#titr_yek_main').is_visible():
                        await news_sorting_toggle.click()
                        await asyncio.sleep(2)
                    
                    # Select the main checkboxes
                    await page.locator('#titr_yek_main').check()
                    await asyncio.sleep(1)
                    await page.locator('#naab_main').check()
                    await asyncio.sleep(1)
                    
                    # Handle category-specific checkboxes
                    for category_id in category_ids:
                        try:
                            # Try to make the category fields visible via JavaScript
                            await page.evaluate("""
                                var metaFields = document.querySelector("#meta_fields_""" + category_id + """");
                                if (metaFields) {
                                    metaFields.style.display = "block";
                                }
                            """)
                            await asyncio.sleep(1)
                            
                            # Check the boxes if they exist
                            titr_yek = page.locator(f'#titr_yek_{category_id}')
                            if await titr_yek.count() > 0:
                                await titr_yek.check()
                                await asyncio.sleep(0.5)
                            
                            naab = page.locator(f'#naab_{category_id}')
                            if await naab.count() > 0:
                                await naab.check()
                                await asyncio.sleep(0.5)
                        except Exception as e:
                            logger.warning(f"Error with category-specific news sorting for {category_id}: {e}")
            except Exception as e:
                logger.warning(f"Error handling News Sorting section: {e}")
            
            # STEP 12: Add tags (hashtags)
            await print_progress("Adding hashtags")
            try:
                # Make sure the tags section is visible
                tags_box = page.locator('#tagsdiv-post_tag')
                if not await tags_box.is_visible():
                    toggle_button = page.locator('#tagsdiv-post_tag .handlediv')
                    if await toggle_button.is_visible():
                        await toggle_button.click()
                        await asyncio.sleep(2)
                
                # Get the hashtags and split them
                hashtags = news_data['hashtags'].split(',') if ',' in news_data['hashtags'] else [news_data['hashtags']]
                
                # Add each hashtag
                for tag in hashtags:
                    tag = tag.strip()
                    if tag:
                        await page.fill('input[name="newtag[post_tag]"]', tag)
                        await asyncio.sleep(1)
                        await page.keyboard.press('Enter')
                        await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"Error adding hashtags: {e}")
            
            # STEP 13: Add SEO keyword
            if news_data['seo_keyword']:
                await print_progress("Adding SEO keyword")
                try:
                    # Try direct interaction first
                    focus_keyword = page.locator(".tagify__input")
                    await focus_keyword.click()
                    await asyncio.sleep(1)
                    await page.keyboard.type(news_data['seo_keyword'])
                    await asyncio.sleep(1)
                    await page.keyboard.press('Enter')
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.warning(f"Standard approach for SEO keyword failed: {e}")
                    
                    # Try JavaScript approach
                    try:
                        await page.evaluate("""
                            const focusKeywordInput = document.querySelector('.tagify__input');
                            if (focusKeywordInput) {
                                focusKeywordInput.focus();
                                const inputEvent = new Event('input', { bubbles: true });
                                focusKeywordInput.textContent = arguments[0];
                                focusKeywordInput.dispatchEvent(inputEvent);
                                
                                const enterEvent = new KeyboardEvent('keydown', {
                                    key: 'Enter',
                                    code: 'Enter',
                                    keyCode: 13,
                                    which: 13,
                                    bubbles: true
                                });
                                focusKeywordInput.dispatchEvent(enterEvent);
                            }
                        """, news_data['seo_keyword'])
                        await asyncio.sleep(2)
                    except Exception as e2:
                        logger.warning(f"JavaScript fallback for SEO keyword failed: {e2}")
            
            # STEP 14: Scroll to top of the page before looking for the publish box
            await print_progress("Scrolling to top of the page")
            try:
                # Scroll to the top of the page
                await page.evaluate("window.scrollTo(0, 0);")
                await asyncio.sleep(2)
                
                # Additional scrolling to ensure we're at the very top
                await page.keyboard.press("Home")
                await asyncio.sleep(2)
                
                logger.info("Successfully scrolled to the top of the page")
            except Exception as e:
                logger.warning(f"Error scrolling to top: {e}")
                # Try another method if the first fails
                try:
                    await page.keyboard.press("Home")
                    await asyncio.sleep(2)
                except Exception as e2:
                    logger.warning(f"Second scrolling attempt failed: {e2}")
            
            # Now make sure the publish box is expanded and save as draft
            await print_progress("Preparing to save as draft")
            try:
                # Ensure the publish box is expanded
                publish_box = page.locator('#submitdiv')
                
                # First check if the publish box is visible
                if not await publish_box.is_visible():
                    logger.info("Publish box not visible, trying to find it")
                    # Try to scroll to it first
                    await page.evaluate("""
                        const publishBox = document.getElementById('submitdiv');
                        if (publishBox) {
                            publishBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    """)
                    await asyncio.sleep(2)
                
                # Now check if the toggle indicator needs to be clicked to expand
                toggle_indicator = publish_box.locator('.handlediv')
                if await toggle_indicator.is_visible():
                    # Check if the box is collapsed by looking for the save-post button visibility
                    save_button = page.locator('#save-post')
                    if not await save_button.is_visible():
                        logger.info("Publish box is collapsed, expanding it")
                        await toggle_indicator.click()
                        await asyncio.sleep(2)
                
                # Make sure the minor-publishing-actions div is visible
                minor_publishing = page.locator('#minor-publishing-actions')
                if not await minor_publishing.is_visible():
                    logger.info("Minor publishing actions not visible, trying to make them visible")
                    await page.evaluate("""
                        const minorPublishing = document.getElementById('minor-publishing-actions');
                        if (minorPublishing) {
                            minorPublishing.style.display = 'block';
                        }
                    """)
                    await asyncio.sleep(1)
                
                # Try clicking the save draft button with multiple approaches
                await print_progress("Clicking save draft button")
                
                # First try: direct click on save-post button
                save_button = page.locator('#save-post')
                if await save_button.is_visible():
                    logger.info("Found #save-post button, clicking it")
                    await save_button.click()
                    await asyncio.sleep(5)
                else:
                    # Second try: look for any button in the save-action area
                    save_action = page.locator('#save-action input[type="submit"]')
                    if await save_action.is_visible():
                        logger.info("Found save action button, clicking it")
                        await save_action.click()
                        await asyncio.sleep(5)
                    else:
                        # Third try: use JavaScript to click the button
                        logger.info("Using JavaScript to find and click save button")
                        clicked = await page.evaluate("""
                            const saveButton = document.getElementById('save-post');
                            if (saveButton) {
                                saveButton.click();
                                return true;
                            }
                            
                            const saveAction = document.querySelector('#save-action input[type="submit"]');
                            if (saveAction) {
                                saveAction.click();
                                return true;
                            }
                            
                            return false;
                        """)
                        
                        if clicked:
                            logger.info("Successfully clicked save button via JavaScript")
                            await asyncio.sleep(5)
                        else:
                            # Fourth try: find by text content
                            logger.warning("Could not find save button by ID, trying by text content")
                            buttons = await page.locator('input[type="submit"]').all()
                            for button in buttons:
                                value = await button.get_attribute('value')
                                if value and ('ذخیره' in value or 'پیش‌نویس' in value):
                                    logger.info(f"Found button with text: {value}")
                                    await button.click()
                                    await asyncio.sleep(5)
                                    break
                
                # Wait for save to complete - look for success message or URL change
                try:
                    await page.wait_for_selector('#message.updated', timeout=10000)
                    logger.info("Save confirmation message found!")
                except Exception as e:
                    logger.warning(f"No confirmation message found: {e}")
                    # Check if URL changed to edit-post format
                    if 'post.php?post=' in page.url and 'action=edit' in page.url:
                        logger.info("URL changed to edit mode, save likely successful")
                    else:
                        logger.warning("Could not confirm if save was successful")
                
                # Final success message
                print("\n✅ News uploaded successfully as draft!")
                
            except Exception as e:
                logger.error(f"Error in save draft process: {e}")
                # Last resort attempt
                try:
                    logger.info("Attempting emergency save with keyboard shortcut")
                    await page.keyboard.press('Control+s')
                    await asyncio.sleep(5)
                    print("\n⚠️ Attempted emergency save with keyboard shortcut")
                except Exception as e2:
                    logger.error(f"Emergency save failed: {e2}")
                    raise
            
            # Wait a moment before closing
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"Upload process error: {e}")
            print(f"\n❌ Error during upload: {e}")
            raise
        finally:
            await browser.close()
            
    return None