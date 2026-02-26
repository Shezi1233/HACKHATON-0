#!/usr/bin/env python3
"""
Gmail Watcher for AI Employee
Monitors Gmail for important messages and creates action items
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime, timezone
import os
import json
import time

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str = None, test_mode: bool = False):
        super().__init__(vault_path, check_interval=120, test_mode=test_mode)  # Check every 2 minutes
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH')
        self.processed_ids = set()
        self.credentials = None
        self.service = None
        self.test_mode = test_mode or os.getenv('TEST_MODE', '').lower() == 'true'

        # Load credentials and build service
        if self.credentials_path and os.path.exists(self.credentials_path):
            try:
                self.credentials = Credentials.from_authorized_user_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/gmail.readonly']
                )
                self.service = build('gmail', 'v1', credentials=self.credentials)
                if self.test_mode:
                    print("MCP CONNECTIVITY: Gmail service initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to load Gmail credentials: {e}")
                if self.test_mode:
                    print(f"MCP CONNECTIVITY: Failed to load Gmail credentials: {e}")
        else:
            self.logger.warning("Gmail credentials not found. Running in simulation mode.")
            if self.test_mode:
                print("MCP CONNECTIVITY: Gmail credentials not found, running in simulation mode")

        # Load previously processed IDs from a file to avoid reprocessing
        processed_file = self.vault_path / '.gmail_processed.json'
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    self.processed_ids = set(json.load(f))
            except Exception as e:
                self.logger.error(f"Failed to load processed Gmail IDs: {e}")

    def save_processed_ids(self):
        """Save processed message IDs to file"""
        processed_file = self.vault_path / '.gmail_processed.json'
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def check_for_updates(self) -> list:
        """Return list of new important emails to process"""
        if not self.service:
            # Simulation mode: return empty list
            self.logger.info("Gmail service not available - simulation mode")
            return []

        try:
            # Query for unread important emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important after:1day'
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed messages
            new_messages = [
                msg for msg in messages
                if msg['id'] not in self.processed_ids
            ]

            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []

    def create_action_file(self, message) -> str:
        """Create .md file in Needs_Action folder for the email"""
        if not self.service:
            # Simulation mode
            self.logger.info(f"Simulating action file creation for message ID: {message.get('id', 'unknown')}")
            # Create a simulated email file
            email_id = message.get('id', 'simulated_' + str(int(time.time())))
            filepath = self.needs_action / f'EMAIL_{email_id}.md'

            content = f'''---
type: email
from: simulated.sender@example.com
subject: Simulated Important Email
received: {datetime.now(timezone.utc).isoformat()}
priority: high
status: pending
---

## Email Content
This is a simulated important email that requires action.

## Suggested Actions
- [ ] Review email content
- [ ] Determine appropriate response
- [ ] Flag for human approval if needed
'''
            filepath.write_text(content)
            self.processed_ids.add(email_id)
            self.save_processed_ids()
            return str(filepath)

        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Extract headers and body
            headers = {}
            for header in msg['payload'].get('headers', []):
                headers[header['name']] = header['value']

            # Get email body
            body = self._extract_body(msg['payload'])

            # Create action file content
            content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {headers.get('Date', datetime.now(timezone.utc).isoformat())}
priority: high
status: pending
gmail_id: {message['id']}
---

## Email Content
{body}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Add to task list if action required
'''
            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'

            filepath.write_text(content)

            # Add to processed IDs to avoid reprocessing
            self.processed_ids.add(message['id'])
            self.save_processed_ids()

            self.logger.info(f"Created action file for email: {headers.get('Subject', 'No Subject')}")

            return str(filepath)

        except Exception as e:
            self.logger.error(f"Error creating action file for message {message['id']}: {e}")
            return None

    def _extract_body(self, payload):
        """Extract email body from payload"""
        # This is a simplified implementation
        # In a full implementation, you'd need to handle different MIME types
        body = "Email body not available in simulation mode"

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    # In a real implementation, you'd decode the base64 data
                    body = part['body'].get('data', 'Email body not available')
                    break
        else:
            # Single part email
            body = payload.get('body', {}).get('data', 'Email body not available')

        return body


def main():
    import sys
    import os
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = "./AI_Employee_Vault"

    # Use credentials file if provided as second argument
    credentials_path = sys.argv[2] if len(sys.argv) > 2 else None
    # Check for test mode flag
    test_mode = '--test' in sys.argv or os.getenv('TEST_MODE', '').lower() == 'true'

    watcher = GmailWatcher(vault_path, credentials_path, test_mode=test_mode)
    watcher.run()


if __name__ == "__main__":
    main()