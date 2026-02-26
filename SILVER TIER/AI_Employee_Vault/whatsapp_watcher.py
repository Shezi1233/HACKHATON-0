#!/usr/bin/env python3
"""
WhatsApp Watcher for AI Employee
Monitors WhatsApp Web for important messages and creates action items
"""
from playwright.sync_api import sync_playwright
from base_watcher import BaseWatcher
from datetime import datetime
import json
import os
from pathlib import Path
import time


class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None, keywords: list = None):
        super().__init__(vault_path, check_interval=30)  # Check every 30 seconds
        self.session_path = Path(session_path or os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session'))
        self.keywords = keywords or [
            'urgent', 'asap', 'invoice', 'payment', 'help', 'problem',
            'question', 'need', 'now', 'immediately', 'critical', 'important'
        ]
        self.processed_messages = set()

        # Create session directory if it doesn't exist
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Load previously processed messages
        processed_file = self.vault_path / '.whatsapp_processed.json'
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                self.processed_messages = set(json.load(f))

    def save_processed_messages(self):
        """Save processed message IDs to file"""
        processed_file = self.vault_path / '.whatsapp_processed.json'
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_messages), f)

    def check_for_updates(self) -> list:
        """Return list of new WhatsApp messages to process"""
        try:
            with sync_playwright() as p:
                # Use persistent context to maintain session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    viewport={'width': 1920, 'height': 1080}
                )

                page = browser.new_page()
                page.goto('https://web.whatsapp.com')

                # Wait for WhatsApp to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=15000)
                except:
                    # If not logged in, we can't proceed
                    self.logger.warning("WhatsApp Web not logged in, skipping check")
                    browser.close()
                    return []

                # Find unread messages based on keywords
                messages_to_process = []

                # Get all chat items
                chat_items = page.query_selector_all('[data-testid="chat-list"] [data-testid="conversation"]')

                for chat_item in chat_items:
                    # Check if chat has unread messages
                    unread_indicator = chat_item.query_selector('[data-testid="default-message-status"]')
                    if unread_indicator:
                        # Extract chat info
                        chat_name_elem = chat_item.query_selector('[title]')
                        if chat_name_elem:
                            chat_name = chat_name_elem.get_attribute('title')

                            # Click on the chat to see messages
                            chat_item.click()
                            page.wait_for_timeout(1000)  # Wait for messages to load

                            # Get recent messages
                            message_bubbles = page.query_selector_all('[data-testid="msg-container"] [data-testid="conversation"]')

                            for msg_bubble in message_bubbles[-5:]:  # Check last 5 messages
                                message_text = msg_bubble.inner_text()

                                # Check if message contains keywords
                                message_lower = message_text.lower()
                                if any(keyword in message_lower for keyword in self.keywords):
                                    # Create a message object to return
                                    message_obj = {
                                        'chat_name': chat_name,
                                        'text': message_text,
                                        'timestamp': datetime.now().isoformat()
                                    }

                                    # Create a unique identifier for this message
                                    msg_id = f"{chat_name}_{hash(message_text)}_{int(time.time())}"

                                    if msg_id not in self.processed_messages:
                                        messages_to_process.append(message_obj)
                                        self.processed_messages.add(msg_id)

                browser.close()
                return messages_to_process

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            return []

    def create_action_file(self, message) -> str:
        """Create .md file in Needs_Action folder for the WhatsApp message"""
        try:
            # Create a unique filename based on the message
            chat_safe = "".join(c for c in message['chat_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = message['timestamp'].replace(':', '-').replace('.', '-')
            filename = f"WHATSAPP_{chat_safe}_{timestamp}.md"
            filepath = self.needs_action / filename

            content = f'''---
type: whatsapp
from: {message['chat_name']}
received: {message['timestamp']}
priority: high
status: pending
---

## WhatsApp Message
{message['text']}

## Suggested Actions
- [ ] Review message content
- [ ] Determine appropriate response
- [ ] Respond to sender
- [ ] Flag for human approval if needed
- [ ] Follow up if required
'''

            filepath.write_text(content)
            self.save_processed_messages()

            self.logger.info(f"Created action file for WhatsApp message from {message['chat_name']}")

            return str(filepath)

        except Exception as e:
            self.logger.error(f"Error creating action file for WhatsApp message: {e}")
            return None


def main():
    import sys
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = "./AI_Employee_Vault"

    # Use session path if provided as second argument
    session_path = sys.argv[2] if len(sys.argv) > 2 else None

    watcher = WhatsAppWatcher(vault_path, session_path)
    watcher.run()


if __name__ == "__main__":
    main()