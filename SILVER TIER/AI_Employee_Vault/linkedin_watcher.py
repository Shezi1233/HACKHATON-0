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


class LinkedInWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None, keywords: list = None):
        super().__init__(vault_path, check_interval=300)  # Check every 5 minutes
        self.session_path = Path(session_path or os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
        self.keywords = keywords or [
            'interest', 'opportunity', 'business', 'project', 'proposal',
            'inquiry', 'contact', 'connect', 'partnership', 'collaboration',
            'consulting', 'service', 'hire', 'recruit', 'job', 'work'
        ]
        self.processed_activities = set()

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
                # Use persistent context to maintain session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    viewport={'width': 1920, 'height': 1080}
                )

                page = browser.new_page()
                page.goto('https://www.linkedin.com/feed/')

                # Wait for LinkedIn to load
                try:
                    # Wait for feed to load or notifications page
                    page.wait_for_selector('nav, .feed-shared-update-v2', timeout=15000)
                except:
                    # If not logged in, we can't proceed
                    self.logger.warning("LinkedIn not logged in, skipping check")
                    browser.close()
                    return []

                # Check for notifications that might contain relevant keywords
                activities_to_process = []

                # Go to notifications page
                try:
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

                # Also check for messages
                try:
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

                browser.close()
                return activities_to_process

        except Exception as e:
            self.logger.error(f"Error checking LinkedIn: {e}")
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

    watcher = LinkedInWatcher(vault_path, session_path)
    watcher.run()


if __name__ == "__main__":
    main()