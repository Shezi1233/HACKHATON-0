#!/usr/bin/env python3
"""
Orchestrator for the AI Employee Bronze Tier
Manages the file watcher and coordinates with Claude Code
"""

import os
import sys
import time
import logging
from pathlib import Path
from filesystem_watcher import FileSystemWatcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AI_Employee_Orchestrator:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.done_dir = self.vault_path / "Done"
        self.inbox_dir = self.vault_path / "Inbox"
        self.approved_dir = self.vault_path / "Approved"

        # Create directories if they don't exist
        self.needs_action_dir.mkdir(exist_ok=True)
        self.done_dir.mkdir(exist_ok=True)
        self.inbox_dir.mkdir(exist_ok=True)
        self.approved_dir.mkdir(exist_ok=True)

        logger.info(f"Initialized orchestrator for vault: {self.vault_path}")

    def monitor_needs_action(self):
        """Monitor the Needs_Action folder for new tasks"""
        needs_action_files = list(self.needs_action_dir.glob("*.md"))
        if needs_action_files:
            logger.info(f"Found {len(needs_action_files)} files in Needs_Action folder")
            for file_path in needs_action_files:
                logger.info(f"  - {file_path.name}")
            # In a full implementation, this would trigger Claude Code
            # For Bronze Tier, we'll simulate this behavior
            self.process_needs_action_files(needs_action_files)
        else:
            logger.info("No files in Needs_Action folder")

    def process_needs_action_files(self, files):
        """Simulate processing of needs action files"""
        for file_path in files:
            logger.info(f"Processing: {file_path.name}")
            # Move to Done folder after "processing"
            done_path = self.done_dir / file_path.name
            try:
                file_path.rename(done_path)
                logger.info(f"Moved {file_path.name} to Done folder")
            except Exception as e:
                logger.error(f"Error moving file {file_path.name}: {e}")

    def run_continuous_monitoring(self):
        """Run continuous monitoring similar to a real AI Employee"""
        logger.info("Starting continuous monitoring...")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                self.monitor_needs_action()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")

def main():
    # Default vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Look for the vault in the current directory
        vault_path = "./AI_Employee_Vault"

    if not Path(vault_path).exists():
        print(f"Error: Vault directory {vault_path} does not exist")
        sys.exit(1)

    orchestrator = AI_Employee_Orchestrator(vault_path)

    print("AI Employee Orchestrator - Bronze Tier")
    print(f"Vault location: {Path(vault_path).absolute()}")
    print("Starting orchestrator...")

    orchestrator.run_continuous_monitoring()

if __name__ == "__main__":
    main()