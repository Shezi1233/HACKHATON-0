"""
Twitter/X Watcher for the Personal AI Employee

Monitors Twitter for mentions, DMs, and relevant activity,
and creates action files in the Needs_Action folder.
"""

import time
import logging
import os
from pathlib import Path
from typing import List, Dict, Any
import tweepy
from base_watcher import BaseWatcher
from datetime import datetime
import json


class TwitterWatcher(BaseWatcher):
    def __init__(self, vault_path: str, bearer_token: str = None, api_key: str = None,
                 api_secret: str = None, access_token: str = None, access_token_secret: str = None,
                 domain: str = 'business', test_mode: bool = False):
        """Initialize Twitter watcher with credentials"""
        super().__init__(vault_path, check_interval=120, domain=domain, test_mode=test_mode)  # Check every 2 minutes
        self.logger = logging.getLogger(self.__class__.__name__)
        self.test_mode = test_mode or os.getenv('TEST_MODE', '').lower() == 'true'

        # Get credentials from environment variables if not provided
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = api_key or os.getenv('TWITTER_API_KEY')
        self.api_secret = api_secret or os.getenv('TWITTER_API_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([self.bearer_token, self.api_key, self.api_secret,
                   self.access_token, self.access_token_secret]):
            if self.test_mode:
                print("MCP CONNECTIVITY: Twitter credentials not fully configured")
            raise ValueError("Twitter credentials not fully configured")

        # Initialize Tweepy client with error handling
        try:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            if self.test_mode:
                print("MCP CONNECTIVITY: Twitter API client initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Twitter API client: {e}")
            if self.test_mode:
                print(f"MCP CONNECTIVITY: Twitter API client failed to initialize: {e}")

        # Store IDs of processed items to avoid duplicates
        self.processed_tweet_ids = set()
        self.processed_dm_ids = set()

        # Keywords to monitor for urgent attention
        self.urgent_keywords = [
            'urgent', 'asap', 'help', 'pay', 'invoice', 'meeting',
            'proposal', 'contract', 'payment', 'price', 'budget'
        ]

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for new mentions, DMs, and relevant activity"""
        updates = []

        try:
            # Get user ID to identify mentions of the account
            user_response = self.client.get_me()
            user_id = user_response.data.id

            # Check for mentions
            mentions = self._get_mentions(user_id, limit=10)
            for mention in mentions:
                if mention['id'] not in self.processed_tweet_ids:
                    updates.append(mention)
                    self.processed_tweet_ids.add(mention['id'])

            # Check for DMs (requires elevated access)
            dms = self._get_direct_messages(limit=10)
            for dm in dms:
                if dm['id'] not in self.processed_dm_ids:
                    updates.append(dm)
                    self.processed_dm_ids.add(dm['id'])

        except Exception as e:
            self.logger.error(f"Error checking Twitter: {e}")

        return updates

    def _get_mentions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent mentions of the user"""
        try:
            tweets = self.client.get_users_mentions(
                id=user_id,
                max_results=min(limit, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                expansions=['author_id'],
                user_fields=['username', 'name', 'verified']
            )

            mentions = []
            if tweets.data:
                users = {user['id']: user for user in tweets.includes.get('users', []) if user}

                for tweet in tweets.data:
                    user = users.get(tweet.author_id)
                    mention_data = {
                        'id': tweet.id,
                        'type': 'twitter_mention',
                        'author': {
                            'id': tweet.author_id,
                            'name': user.name if user else 'Unknown',
                            'username': user.username if user else 'unknown',
                            'verified': user.verified if user else False
                        },
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'metrics': tweet.public_metrics if tweet.public_metrics else {},
                        'is_urgent': any(keyword in tweet.text.lower() for keyword in self.urgent_keywords)
                    }
                    mentions.append(mention_data)

            return mentions
        except Exception as e:
            self.logger.error(f"Error fetching mentions: {e}")
            return []

    def _get_direct_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent direct messages (Note: Twitter API v2 doesn't provide DM access without enterprise access)"""
        # For now, returning empty list as DM access requires enterprise access in Twitter API v2
        # This is a placeholder for when DM access is available
        self.logger.info("Direct message monitoring requires enterprise Twitter API access")
        return []

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create a markdown file in the Needs_Action folder for the Twitter activity"""
        # Determine filename based on item type
        if item['type'] == 'twitter_mention':
            filename = f"TWITTER_MENTION_{item['author']['username']}_{item['id']}.md"
        else:
            filename = f"TWITTER_DM_{item['author']['username']}_{item['id']}.md"

        filepath = self.needs_action / filename

        # Determine if this requires immediate attention
        priority = "high" if item.get('is_urgent', False) else "normal"

        # Create content for the action file
        content = f"""---
type: {item['type']}
source: twitter
author: {item['author']['name']} (@{item['author']['username']})
author_id: {item['author']['id']}
tweet_id: {item['id']}
created_at: {item['created_at']}
priority: {priority}
status: pending
urgent: {item.get('is_urgent', False)}
---

## Twitter Activity

**From:** {item['author']['name']} (@{item['author']['username']})
**When:** {item['created_at']}
**Verified Account:** {item['author']['verified']}
**Tweet:** {item['text']}

## Engagement Metrics
{self._format_metrics(item.get('metrics', {}))}

## Suggested Actions
- [ ] Review tweet content
- [ ] Respond appropriately following Company_Handbook.md guidelines
- [ ] Flag for human approval if payment or sensitive information mentioned
- [ ] Archive after processing

## Context
This Twitter activity has been detected by the Twitter Watcher and requires attention.
"""

        filepath.write_text(content)
        self.logger.info(f"Created action file: {filepath}")
        return filepath

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format Twitter engagement metrics for display"""
        if not metrics:
            return "No metrics available"

        formatted = []
        if 'like_count' in metrics:
            formatted.append(f"- Likes: {metrics['like_count']}")
        if 'retweet_count' in metrics:
            formatted.append(f"- Retweets: {metrics['retweet_count']}")
        if 'reply_count' in metrics:
            formatted.append(f"- Replies: {metrics['reply_count']}")
        if 'quote_count' in metrics:
            formatted.append(f"- Quotes: {metrics['quote_count']}")

        return "\n".join(formatted) if formatted else "No metrics available"

    def run(self):
        """Main run loop for the Twitter watcher"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Checking Twitter every {self.check_interval} seconds')

        # Load previously processed IDs from a file to avoid reprocessing after restart
        processed_file = self.vault_path / '.twitter_processed.json'
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_tweet_ids = set(data.get('tweets', []))
                    self.processed_dm_ids = set(data.get('dms', []))
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
                'tweets': list(self.processed_tweet_ids),
                'dms': list(self.processed_dm_ids)
            }
            with open(processed_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error saving processed IDs: {e}")


    def run(self):
        """Main run loop for the Twitter watcher"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Checking Twitter every {self.check_interval} seconds')

        # Load previously processed IDs from a file to avoid reprocessing after restart
        processed_file = self.vault_path / '.twitter_processed.json'
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_tweet_ids = set(data.get('tweets', []))
                    self.processed_dm_ids = set(data.get('dms', []))
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

    parser = argparse.ArgumentParser(description='Twitter Watcher for AI Employee')
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
    watcher = TwitterWatcher(vault_path=args.vault_path, test_mode=test_mode)
    watcher.run()