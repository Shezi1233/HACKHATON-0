#!/usr/bin/env python3
"""
LinkedIn Watcher for AI Employee
Monitors LinkedIn for mentions, messages and updates business opportunities
"""
from playwright.sync_api import sync_playwright
from base_watcher import BaseWatcher
from datetime import datetime
import json
import os
from pathlib import Path
import time
import os


class LinkedInWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None, keywords: list = None, test_mode: bool = False):
        super().__init__(vault_path, check_interval=300)  # Check every 5 minutes
        self.session_path = Path(session_path or os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
        self.keywords = keywords or [
            'interest', 'opportunity', 'business', 'project', 'proposal',
            'inquiry', 'contact', 'connect', 'partnership', 'collaboration',
            'consulting', 'service', 'hire', 'recruit', 'job', 'work'
        ]
        self.processed_activities = set()
        self.test_mode = test_mode or os.getenv('TEST_MODE', '').lower() == 'true'

        # Create session directory if it doesn't exist
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Load previously processed activities
        processed_file = self.vault_path / '.linkedin_processed.json'
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                self.processed_activities = set(json.load(f))

    def save_processed_activities(self):
        """Save processed activity IDs to file"""
        processed_file = self.vault_path / '.linkedin_processed.json'
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_activities), f)

    def check_for_updates(self) -> list:
        """Return list of new LinkedIn activities to process"""
        try:
            with sync_playwright() as p:
                # Determine headless mode based on test_mode
                headless_mode = not self.test_mode  # Show browser in test mode for authentication setup
                if self.test_mode:
                    print("BROWSER LAUNCH: Starting LinkedIn browser for authentication setup...")

                # Use persistent context to maintain session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=headless_mode,
                    viewport={'width': 1920, 'height': 1080}
                )

                if self.test_mode:
                    print("BROWSER LAUNCH: LinkedIn browser started with persistent context")

                page = browser.new_page()

                # Try to navigate to LinkedIn and check if user is logged in
                page.goto('https://www.linkedin.com/feed/')

                if self.test_mode:
                    print("LOGIN DETECTION: Attempting to navigate to LinkedIn feed...")

                # Wait for the page to load and check for login status
                try:
                    # Check if we're on the feed (logged in) or login page (not logged in)
                    # Look for profile avatar or feed elements to confirm login
                    profile_avatar_selector = 'img[alt*="Photo"], .global-nav__me-photo, [data-test-id="profile-nav-item"]'
                    feed_selector = '[data-test-id="feed-container"], .feed-shared-update-v2, nav'

                    # Wait for either profile element (logged in) or feed elements
                    page.wait_for_timeout(3000)  # Wait for page to load

                    # Check if logged in by looking for profile elements
                    is_logged_in = page.query_selector(profile_avatar_selector) is not None or \
                                   page.query_selector(feed_selector) is not None

                    if not is_logged_in:
                        # Check if it's a login page
                        login_elements = page.query_selector('input[name="session_key"]')
                        if login_elements:
                            if self.test_mode:
                                print("LOGIN DETECTION: LinkedIn requires login. Please log in manually.")
                                print("LOGIN DETECTION: Navigate to the feed and log in when browser is displayed.")
                                input("Press Enter after you have logged in and are on the feed page...")
                            else:
                                self.logger.warning("LinkedIn not logged in, skipping check")
                                browser.close()
                                return []
                    else:
                        if self.test_mode:
                            print("LOGIN DETECTION: LinkedIn authentication confirmed!")

                except Exception as login_check_error:
                    if self.test_mode:
                        print(f"LOGIN DETECTION: Error during login check: {login_check_error}")
                    self.logger.warning("Could not confirm LinkedIn login status, proceeding anyway")

                # Check for notifications that might contain relevant keywords
                activities_to_process = []

                # Go to notifications page
                try:
                    if self.test_mode:
                        print("CHECKING: Going to LinkedIn notifications page...")
                    page.goto('https://www.linkedin.com/notifications/')
                    page.wait_for_timeout(2000)

                    # Look for recent notifications
                    notification_items = page.query_selector_all('li[tabindex="0"]')

                    for notification_item in notification_items[:10]:  # Check top 10 notifications
                        notification_text = notification_item.inner_text()

                        # Check if notification contains relevant keywords
                        notification_lower = notification_text.lower()
                        if any(keyword in notification_lower for keyword in self.keywords):
                            activity_obj = {
                                'type': 'notification',
                                'content': notification_text,
                                'timestamp': datetime.now().isoformat()
                            }

                            # Create a unique identifier for this activity
                            activity_id = f"notification_{hash(notification_text)}_{int(time.time())}"

                            if activity_id not in self.processed_activities:
                                activities_to_process.append(activity_obj)
                                self.processed_activities.add(activity_id)

                except Exception as e:
                    self.logger.warning(f"Could not check notifications: {e}")
                    if self.test_mode:
                        print(f"CHECKING: Error checking notifications: {e}")

                # Also check for messages
                try:
                    if self.test_mode:
                        print("CHECKING: Going to LinkedIn messages page...")
                    page.goto('https://www.linkedin.com/messaging/')
                    page.wait_for_timeout(2000)

                    # Look for unread messages
                    unread_messages = page.query_selector_all('[data-test-is-read="false"]')

                    for msg in unread_messages:
                        message_text = msg.inner_text()

                        # Check if message contains relevant keywords
                        message_lower = message_text.lower()
                        if any(keyword in message_lower for keyword in self.keywords):
                            activity_obj = {
                                'type': 'message',
                                'content': message_text,
                                'timestamp': datetime.now().isoformat()
                            }

                            # Create a unique identifier for this activity
                            activity_id = f"message_{hash(message_text)}_{int(time.time())}"

                            if activity_id not in self.processed_activities:
                                activities_to_process.append(activity_obj)
                                self.processed_activities.add(activity_id)

                except Exception as e:
                    self.logger.warning(f"Could not check messages: {e}")
                    if self.test_mode:
                        print(f"CHECKING: Error checking messages: {e}")

                browser.close()

                if self.test_mode:
                    print(f"CHECKING: Found {len(activities_to_process)} activities to process")

                return activities_to_process

        except Exception as e:
            self.logger.error(f"Error checking LinkedIn: {e}")
            if self.test_mode:
                print(f"ERROR: LinkedIn check failed with error: {e}")
            return []

    def create_action_file(self, activity) -> str:
        """Create .md file in Needs_Action folder for the LinkedIn activity"""
        try:
            # Create a unique filename based on the activity
            activity_type = activity['type']
            timestamp = activity['timestamp'].replace(':', '-').replace('.', '-')
            filename = f"LINKEDIN_{activity_type}_{timestamp}.md"
            filepath = self.needs_action / filename

            content = f'''---
type: linkedin_{activity_type}
received: {activity['timestamp']}
priority: medium
status: pending
---

## LinkedIn {activity['type'].title()} Activity
{activity['content']}

## Suggested Actions
- [ ] Review the LinkedIn activity
- [ ] Determine business relevance
- [ ] Respond appropriately if needed
- [ ] Follow up on business opportunities
- [ ] Flag for human review if important
'''

            filepath.write_text(content)
            self.save_processed_activities()

            self.logger.info(f"Created action file for LinkedIn {activity['type']} activity")

            return str(filepath)

        except Exception as e:
            self.logger.error(f"Error creating action file for LinkedIn activity: {e}")
            return None


def main():
    import sys
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = "./AI_Employee_Vault"

    # Use session path if provided as second argument
    session_path = sys.argv[2] if len(sys.argv) > 2 else None
    # Check for test mode flag
    test_mode = '--test' in sys.argv or os.getenv('TEST_MODE', '').lower() == 'true'

    watcher = LinkedInWatcher(vault_path, session_path, test_mode=test_mode)
    watcher.run()


if __name__ == "__main__":
    main()