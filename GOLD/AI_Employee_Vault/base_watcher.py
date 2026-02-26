import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60, domain: str = 'shared', test_mode: bool = False):
        self.vault_path = Path(vault_path)
        self.domain = domain.lower()
        self.test_mode = test_mode

        # Set up domain-specific paths
        if self.domain == 'personal':
            self.needs_action = self.vault_path / 'Personal' / 'Needs_Action'
        elif self.domain == 'business':
            self.needs_action = self.vault_path / 'Business' / 'Needs_Action'
        else:  # shared domain
            self.needs_action = self.vault_path / 'Needs_Action'

        # Create the needs_action directory if it doesn't exist
        self.needs_action.mkdir(parents=True, exist_ok=True)

        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in appropriate Needs_Action folder based on domain'''
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__} for domain: {self.domain}')

        # For test mode, run only once
        if self.test_mode:
            self.logger.info("Running in TEST MODE - single execution cycle")
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
                self.logger.info(f"TEST MODE: Completed check. Processed {len(items)} items.")
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
                print(f"TEST ERROR: {e}")
        else:
            # Production mode - run continuously
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        self.create_action_file(item)
                except Exception as e:
                    self.logger.error(f'Error in {self.__class__.__name__}: {e}')
                time.sleep(self.check_interval)