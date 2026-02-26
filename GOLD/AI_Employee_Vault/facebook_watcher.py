"""
Facebook/Instagram Watcher for the Personal AI Employee

Monitors Facebook page and Instagram for mentions, comments, and messages,
and creates action files in the Needs_Action folder.
"""

import time
import logging
import os
from pathlib import Path
from typing import List, Dict, Any
from base_watcher import BaseWatcher
from datetime import datetime
import requests
import json


class FacebookWatcher(BaseWatcher):
    def __init__(self, vault_path: str, access_token: str = None, page_id: str = None, domain: str = 'business', test_mode: bool = False):
        """Initialize Facebook watcher with credentials"""
        super().__init__(vault_path, check_interval=180, domain=domain, test_mode=test_mode)  # Check every 3 minutes
        self.logger = logging.getLogger(self.__class__.__name__)
        self.test_mode = test_mode or os.getenv('TEST_MODE', '').lower() == 'true'

        # Get credentials from environment variables if not provided
        self.access_token = access_token or os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = page_id or os.getenv('FACEBOOK_PAGE_ID')

        if not self.access_token:
            if self.test_mode:
                print("MCP CONNECTIVITY: Facebook access token not configured")
            raise ValueError("Facebook access token not configured")

        # Store IDs of processed items to avoid duplicates
        self.processed_comment_ids = set()
        self.processed_message_ids = set()
        self.processed_post_ids = set()

        # Keywords to monitor for urgent attention
        self.urgent_keywords = [
            'urgent', 'asap', 'help', 'pay', 'invoice', 'meeting',
            'proposal', 'contract', 'payment', 'price', 'budget', 'order'
        ]

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for new posts, comments, and messages on Facebook"""
        updates = []

        try:
            # Check for new posts on the page
            posts = self._get_page_posts(limit=5)
            for post in posts:
                if post['id'] not in self.processed_post_ids:
                    updates.append(post)
                    self.processed_post_ids.add(post['id'])

            # Check for comments on page posts
            comments = self._get_page_comments(limit=10)
            for comment in comments:
                if comment['id'] not in self.processed_comment_ids:
                    updates.append(comment)
                    self.processed_comment_ids.add(comment['id'])

            # Check for page messages
            messages = self._get_page_messages(limit=10)
            for message in messages:
                if message['id'] not in self.processed_message_ids:
                    updates.append(message)
                    self.processed_message_ids.add(message['id'])

        except Exception as e:
            self.logger.error(f"Error checking Facebook: {e}")

        return updates

    def facebook_api_get(self, endpoint: str, params: dict = None) -> Dict:
        """Make a GET request to Facebook Graph API"""
        if params is None:
            params = {}

        # Add access token to params
        params['access_token'] = self.access_token

        url = f"https://graph.facebook.com/v18.0/{endpoint}"

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def facebook_api_post(self, endpoint: str, data: dict = None) -> Dict:
        """Make a POST request to Facebook Graph API"""
        if data is None:
            data = {}

        # Add access token to data
        data['access_token'] = self.access_token

        url = f"https://graph.facebook.com/v18.0/{endpoint}"

        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()

    def _get_page_posts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch recent posts from the Facebook page"""
        try:
            if not self.page_id:
                self.logger.warning("Facebook page ID not configured, cannot fetch posts")
                return []

            posts_data = self.facebook_api_get(
                f"{self.page_id}/posts",
                params={
                    'fields': 'id,message,created_time,from,permalink_url,full_picture,shares,likes.summary(true),comments.summary(true)',
                    'limit': limit
                }
            )

            posts = []
            if 'data' in posts_data:
                for post in posts_data['data']:
                    post_data = {
                        'id': post['id'],
                        'type': 'facebook_post',
                        'author': post.get('from', {}),
                        'message': post.get('message', ''),
                        'created_time': post.get('created_time'),
                        'permalink_url': post.get('permalink_url'),
                        'shares_count': post.get('shares', {}).get('count', 0),
                        'likes_count': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                        'comments_count': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                        'is_urgent': any(keyword in post.get('message', '').lower() for keyword in self.urgent_keywords)
                    }
                    posts.append(post_data)

            return posts
        except Exception as e:
            self.logger.error(f"Error fetching Facebook posts: {e}")
            return []

    def _get_page_comments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent comments on the Facebook page's posts"""
        try:
            if not self.page_id:
                self.logger.warning("Facebook page ID not configured, cannot fetch comments")
                return []

            # Get comments on the page's posts
            comments_data = self.facebook_api_get(
                f"{self.page_id}/comments",
                params={
                    'fields': 'id,from,message,created_time,parent,can_comment,like_count',
                    'limit': limit
                }
            )

            comments = []
            if 'data' in comments_data:
                for comment in comments_data['data']:
                    comment_data = {
                        'id': comment['id'],
                        'type': 'facebook_comment',
                        'author': comment.get('from', {}),
                        'message': comment['message'],
                        'created_time': comment.get('created_time'),
                        'parent_post_id': comment.get('parent', {}).get('id') if comment.get('parent') else None,
                        'like_count': comment.get('like_count', 0),
                        'is_urgent': any(keyword in comment['message'].lower() for keyword in self.urgent_keywords)
                    }
                    comments.append(comment_data)

            return comments
        except Exception as e:
            self.logger.error(f"Error fetching Facebook comments: {e}")
            return []

    def _get_page_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent messages sent to the Facebook page"""
        try:
            if not self.page_id:
                self.logger.warning("Facebook page ID not configured, cannot fetch messages")
                return []

            # Get conversations (threads) with the page
            conversations_data = self.facebook_api_get(
                f"{self.page_id}/conversations",
                params={
                    'fields': 'id,link,updated_time,snippet,participants',
                    'limit': limit
                }
            )

            messages = []
            if 'data' in conversations_data:
                for conversation in conversations_data['data']:
                    message_data = {
                        'id': conversation['id'],
                        'type': 'facebook_message',
                        'snippet': conversation.get('snippet', ''),
                        'updated_time': conversation.get('updated_time'),
                        'link': conversation.get('link'),
                        'participants': conversation.get('participants', {}).get('data', []),
                        'is_urgent': any(keyword in conversation.get('snippet', '').lower() for keyword in self.urgent_keywords)
                    }
                    messages.append(message_data)

            return messages
        except Exception as e:
            self.logger.error(f"Error fetching Facebook messages: {e}")
            return []

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create a markdown file in the Needs_Action folder for the Facebook activity"""
        # Determine filename based on item type
        if item['type'] == 'facebook_post':
            filename = f"FACEBOOK_POST_{item['id'].replace(':', '_')}.md"
        elif item['type'] == 'facebook_comment':
            filename = f"FACEBOOK_COMMENT_{item['id'].replace(':', '_')}.md"
        else:  # facebook_message
            filename = f"FACEBOOK_MESSAGE_{item['id'].replace(':', '_')}.md"

        filepath = self.needs_action / filename

        # Determine if this requires immediate attention
        priority = "high" if item.get('is_urgent', False) else "normal"

        # Create content for the action file
        content = self._generate_content(item, priority)
        filepath.write_text(content)
        self.logger.info(f"Created action file: {filepath}")
        return filepath

    def _generate_content(self, item: Dict[str, Any], priority: str) -> str:
        """Generate markdown content for the action file based on item type"""
        base_content = f"""---
type: {item['type']}
source: facebook
item_id: {item['id']}
created_at: {item.get('created_time', item.get('updated_time', datetime.now().isoformat()))}
priority: {priority}
status: pending
urgent: {item.get('is_urgent', False)}
---

## Facebook Activity

"""

        if item['type'] == 'facebook_post':
            author_name = item['author'].get('name', 'Unknown') if 'author' in item else 'Unknown'
            author_id = item['author'].get('id', 'Unknown') if 'author' in item else 'Unknown'

            base_content += f"""**Post By:** {author_name} (ID: {author_id})
**When:** {item.get('created_time', 'Unknown')}
**Post:** {item.get('message', 'No message')}

## Engagement Metrics
- Likes: {item.get('likes_count', 0)}
- Comments: {item.get('comments_count', 0)}
- Shares: {item.get('shares_count', 0)}
- Permalink: {item.get('permalink_url', 'Not available')}

## Suggested Actions
- [ ] Review post content
- [ ] Respond appropriately following Company_Handbook.md guidelines
- [ ] Flag for human approval if payment or sensitive information mentioned
- [ ] Archive after processing
"""

        elif item['type'] == 'facebook_comment':
            author_name = item['author'].get('name', 'Unknown') if 'author' in item else 'Unknown'
            author_id = item['author'].get('id', 'Unknown') if 'author' in item else 'Unknown'

            base_content += f"""**Comment By:** {author_name} (ID: {author_id})
**When:** {item.get('created_time', 'Unknown')}
**On Post:** {item.get('parent_post_id', 'Unknown')}
**Comment:** {item['message']}

## Engagement Metrics
- Likes on comment: {item.get('like_count', 0)}

## Suggested Actions
- [ ] Review comment content
- [ ] Respond appropriately following Company_Handbook.md guidelines
- [ ] Flag for human approval if payment or sensitive information mentioned
- [ ] Archive after processing
"""

        else:  # facebook_message
            participant_names = [p.get('name', 'Unknown') for p in item.get('participants', [])]

            base_content += f"""**Message Thread With:** {', '.join(participant_names)}
**Last Updated:** {item.get('updated_time', 'Unknown')}
**Snippet:** {item.get('snippet', 'No snippet')}
**Link:** {item.get('link', 'Not available')}

## Suggested Actions
- [ ] Review message content
- [ ] Respond appropriately following Company_Handbook.md guidelines
- [ ] Flag for human approval if payment or sensitive information mentioned
- [ ] Archive after processing
"""

        base_content += f"""

## Context
This Facebook activity has been detected by the Facebook Watcher and requires attention.
"""

        return base_content

    def run(self):
        """Main run loop for the Facebook watcher"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Checking Facebook every {self.check_interval} seconds')

        # Load previously processed IDs from a file to avoid reprocessing after restart
        processed_file = self.vault_path / '.facebook_processed.json'
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_post_ids = set(data.get('posts', []))
                    self.processed_comment_ids = set(data.get('comments', []))
                    self.processed_message_ids = set(data.get('messages', []))
            except Exception as e:
                self.logger.error(f"Error loading processed IDs: {e}")

        while True:
            try:
                items = self.check_for_updates()

                for item in items:
                    self.create_action_file(item)

                    # Save processed IDs periodically
                    self._save_processed_ids(processed_file)

            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')

            time.sleep(self.check_interval)

    def _save_processed_ids(self, processed_file: Path):
        """Save processed IDs to file to maintain state across restarts"""
        try:
            data = {
                'posts': list(self.processed_post_ids),
                'comments': list(self.processed_comment_ids),
                'messages': list(self.processed_message_ids)
            }
            with open(processed_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error saving processed IDs: {e}")


    def run(self):
        """Main run loop for the Facebook watcher"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Checking Facebook every {self.check_interval} seconds')

        # Load previously processed IDs from a file to avoid reprocessing after restart
        processed_file = self.vault_path / '.facebook_processed.json'
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_post_ids = set(data.get('posts', []))
                    self.processed_comment_ids = set(data.get('comments', []))
                    self.processed_message_ids = set(data.get('messages', []))
            except Exception as e:
                self.logger.error(f"Error loading processed IDs: {e}")

        # For test mode, run only once
        if self.test_mode:
            self.logger.info("Running in TEST MODE - single execution cycle")
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
                # Save processed IDs after test run
                self._save_processed_ids(processed_file)
                self.logger.info(f"TEST MODE: Completed check. Processed {len(items)} items.")
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
                if self.test_mode:
                    print(f"TEST ERROR: {e}")
        else:
            # Production mode - run continuously
            while True:
                try:
                    items = self.check_for_updates()

                    for item in items:
                        self.create_action_file(item)

                        # Save processed IDs periodically
                        self._save_processed_ids(processed_file)

                except Exception as e:
                    self.logger.error(f'Error in {self.__class__.__name__}: {e}')

                time.sleep(self.check_interval)


if __name__ == "__main__":
    # Example usage
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Facebook Watcher for AI Employee')
    parser.add_argument('--vault-path', type=str, required=True, help='Path to the Obsidian vault')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize and run the watcher
    test_mode = args.test or os.getenv('TEST_MODE', '').lower() == 'true'
    watcher = FacebookWatcher(vault_path=args.vault_path, test_mode=test_mode)
    watcher.run()