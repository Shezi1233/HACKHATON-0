#!/usr/bin/env python3
"""
Master Orchestrator for AI Employee Silver Tier
Manages all components: watchers, reasoning, scheduling, approvals
"""

import os
import sys
import time
import logging
from pathlib import Path
from threading import Thread
from datetime import datetime

# Import all components
from orchestrator import AI_Employee_Orchestrator
from filesystem_watcher import FileSystemWatcher
from gmail_watcher import GmailWatcher
from whatsapp_watcher import WhatsAppWatcher
from linkedin_watcher import LinkedInWatcher
from scheduler import AIEmployeeScheduler


class MasterOrchestrator:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Initialize all components
        self.ai_orchestrator = AI_Employee_Orchestrator(vault_path)
        self.file_watcher = FileSystemWatcher(vault_path)
        self.gmail_watcher = None
        self.whatsapp_watcher = None
        self.linkedin_watcher = None
        self.scheduler = AIEmployeeScheduler(vault_path)

        # Threads for each component
        self.threads = []
        self.running = False

    def start_watchers(self):
        """Start all watcher threads"""
        # Start filesystem watcher
        fs_thread = Thread(target=self.run_filesystem_watcher, daemon=True)
        fs_thread.start()
        self.threads.append(fs_thread)

        # Start Gmail watcher if credentials are available
        if self.check_gmail_credentials():
            self.gmail_watcher = GmailWatcher(self.vault_path)
            gmail_thread = Thread(target=self.run_gmail_watcher, daemon=True)
            gmail_thread.start()
            self.threads.append(gmail_thread)
        else:
            self.logger.warning("Gmail credentials not found, skipping Gmail watcher")

        # Start WhatsApp watcher if Playwright is available
        try:
            from playwright.sync_api import sync_playwright
            self.whatsapp_watcher = WhatsAppWatcher(self.vault_path)
            whatsapp_thread = Thread(target=self.run_whatsapp_watcher, daemon=True)
            whatsapp_thread.start()
            self.threads.append(whatsapp_thread)
        except ImportError:
            self.logger.warning("Playwright not installed, skipping WhatsApp watcher")

        # Start LinkedIn watcher if Playwright is available
        try:
            from playwright.sync_api import sync_playwright
            self.linkedin_watcher = LinkedInWatcher(self.vault_path)
            linkedin_thread = Thread(target=self.run_linkedin_watcher, daemon=True)
            linkedin_thread.start()
            self.threads.append(linkedin_thread)
        except ImportError:
            self.logger.warning("Playwright not installed, skipping LinkedIn watcher")

        self.logger.info("Started all available watcher threads")

    def check_gmail_credentials(self):
        """Check if Gmail credentials are available"""
        cred_path = os.getenv('GMAIL_CREDENTIALS_PATH')
        if cred_path and Path(cred_path).exists():
            return True
        # Also check for a default credentials file
        default_cred = self.vault_path / 'gmail_credentials.json'
        return default_cred.exists()

    def run_filesystem_watcher(self):
        """Run the filesystem watcher in a thread"""
        self.file_watcher.run()

    def run_gmail_watcher(self):
        """Run the Gmail watcher in a thread"""
        if self.gmail_watcher:
            self.gmail_watcher.run()

    def run_whatsapp_watcher(self):
        """Run the WhatsApp watcher in a thread"""
        if self.whatsapp_watcher:
            self.whatsapp_watcher.run()

    def run_linkedin_watcher(self):
        """Run the LinkedIn watcher in a thread"""
        if self.linkedin_watcher:
            self.linkedin_watcher.run()

    def start_scheduler(self):
        """Start the scheduler in a thread"""
        scheduler_thread = Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        self.threads.append(scheduler_thread)

        self.logger.info("Started scheduler thread")

    def run_scheduler(self):
        """Run the scheduler in a thread"""
        self.scheduler.run_scheduler()

    def start_main_orchestrator(self):
        """Start the main orchestrator in a thread"""
        main_thread = Thread(target=self.run_main_orchestrator, daemon=True)
        main_thread.start()
        self.threads.append(main_thread)

        self.logger.info("Started main orchestrator thread")

    def run_main_orchestrator(self):
        """Run the main orchestrator in a thread"""
        self.ai_orchestrator.run_continuous_monitoring()

    def run_master(self):
        """Run the master orchestrator"""
        self.logger.info("Starting Master Orchestrator for AI Employee - Silver Tier")
        self.logger.info(f"Vault location: {self.vault_path.absolute()}")

        # Start all components
        self.start_watchers()
        self.start_scheduler()
        self.start_main_orchestrator()

        self.running = True
        self.logger.info("All components started. Master Orchestrator is running.")
        self.logger.info("Press Ctrl+C to stop all components")

        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Master Orchestrator stopping...")
            self.running = False

    def stop(self):
        """Stop the master orchestrator"""
        self.running = False
        self.logger.info("Master Orchestrator stopped")


def main():
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = "./AI_Employee_Vault"

    if not Path(vault_path).exists():
        print(f"Error: Vault directory {vault_path} does not exist")
        sys.exit(1)

    master_orchestrator = MasterOrchestrator(vault_path)

    print("AI Employee Master Orchestrator - Silver Tier")
    print(f"Vault location: {Path(vault_path).absolute()}")
    print("Starting master orchestrator with all components...")

    master_orchestrator.run_master()


if __name__ == "__main__":
    main()