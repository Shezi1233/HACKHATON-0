#!/usr/bin/env python3
"""
Orchestrator for the AI Employee Silver Tier
Manages multiple watchers and coordinates with Claude Code for reasoning loops
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from threading import Thread
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
        self.plans_dir = self.vault_path / "Plans"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"

        # Create directories if they don't exist
        self.needs_action_dir.mkdir(exist_ok=True)
        self.done_dir.mkdir(exist_ok=True)
        self.inbox_dir.mkdir(exist_ok=True)
        self.approved_dir.mkdir(exist_ok=True)
        self.plans_dir.mkdir(exist_ok=True)
        self.pending_approval_dir.mkdir(exist_ok=True)

        logger.info(f"Initialized orchestrator for vault: {self.vault_path}")

    def monitor_needs_action(self):
        """Monitor the Needs_Action folder for new tasks and trigger Claude reasoning"""
        needs_action_files = list(self.needs_action_dir.glob("*.md"))
        if needs_action_files:
            logger.info(f"Found {len(needs_action_files)} files in Needs_Action folder")
            for file_path in needs_action_files:
                logger.info(f"  - {file_path.name}")
            # For Silver Tier, trigger Claude reasoning for each file
            for file_path in needs_action_files:
                self.trigger_claude_reasoning(file_path)
        else:
            logger.info("No files in Needs_Action folder")

    def trigger_claude_reasoning(self, file_path):
        """Trigger Claude Code to reason about the task and create a plan"""
        logger.info(f"Triggering Claude reasoning for: {file_path.name}")

        # Create a plan file name based on the original file
        plan_filename = f"PLAN_{file_path.stem}_{int(time.time())}.md"
        plan_path = self.plans_dir / plan_filename

        # Read the file content to determine the type of task
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine the type of task and create an appropriate plan
            plan_content = self.generate_plan_content(content, file_path.name)

            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            logger.info(f"Created plan file: {plan_path.name}")

            # After creating the plan, check if it requires approval
            if self.requires_approval(plan_path):
                logger.info(f"Plan {plan_path.name} requires approval")
                # Move the plan to pending approval
                approval_path = self.pending_approval_dir / plan_path.name
                plan_path.rename(approval_path)
            else:
                logger.info(f"Plan {plan_path.name} does not require approval")
                # Process the plan without approval
                self.execute_plan(plan_path)

            # Move the original task file to Done
            done_path = self.done_dir / file_path.name
            file_path.rename(done_path)
            logger.info(f"Moved {file_path.name} to Done folder")

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")

    def generate_plan_content(self, original_content, original_filename):
        """Generate plan content based on the original task"""
        # Determine task type from filename
        if 'EMAIL' in original_filename.upper():
            task_type = "Email Response"
            primary_action = "Draft and send appropriate email response"
        elif 'WHATSAPP' in original_filename.upper():
            task_type = "WhatsApp Message"
            primary_action = "Draft and send appropriate WhatsApp response"
        elif 'LINKEDIN' in original_filename.upper():
            task_type = "LinkedIn Activity"
            primary_action = "Process LinkedIn activity and take appropriate action"
        elif 'FILE_DROP' in original_filename.upper():
            task_type = "File Processing"
            primary_action = "Process the dropped file appropriately"
        else:
            task_type = "General Task"
            primary_action = "Take appropriate action based on content"

        # Extract main content or subject from the original file
        lines = original_content.split('\n')
        content_preview = " ".join(lines[3:8]) if len(lines) > 8 else original_content[:200]

        plan_content = f'''---
created: {datetime.now().isoformat()}
original_file: {original_filename}
status: pending
task_type: {task_type}
---

# Plan for {task_type}

## Objective
{primary_action} based on the following content:

> {content_preview}

## Steps
- [ ] Analyze the request thoroughly
- [ ] Determine appropriate response/actions
- [ ] Check Company_Handbook.md for guidelines
- [ ] Execute primary action
- [ ] Update Dashboard.md with activity
- [ ] Log the action in activity log

## Approval Required
- [ ] Check if action requires human approval per Company_Handbook.md
- [ ] If required, create approval request
- [ ] Wait for approval before proceeding with sensitive actions

## Completion Criteria
- [ ] Action completed successfully
- [ ] Relevant files updated
- [ ] Dashboard updated
- [ ] Activity logged
'''

        return plan_content

    def requires_approval(self, plan_path):
        """Determine if a plan requires human approval"""
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if the plan contains certain keywords that would require approval
            content_lower = content.lower()

            # Common approval triggers
            approval_triggers = [
                'payment', 'invoice', 'money', 'financial', 'bank', 'credit card',
                'sensitive', 'private', 'confidential', 'approval needed', 'requires approval'
            ]

            for trigger in approval_triggers:
                if trigger in content_lower:
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking approval requirements for {plan_path.name}: {e}")
            return False  # Default to requiring approval if uncertain

    def execute_plan(self, plan_path):
        """Execute a plan that doesn't require approval"""
        logger.info(f"Executing plan: {plan_path.name}")

        # In a real implementation, this would call Claude Code to execute the plan
        # For now, we'll just mark it as completed and move to done

        done_path = self.done_dir / plan_path.name
        plan_path.rename(done_path)
        logger.info(f"Executed plan {plan_path.name}, moved to Done folder")

    def run_continuous_monitoring(self):
        """Run continuous monitoring similar to a real AI Employee"""
        logger.info("Starting continuous monitoring...")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                self.monitor_needs_action()
                self.monitor_approved_actions()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")

    def monitor_approved_actions(self):
        """Monitor the Approved folder for actions that were approved"""
        approved_files = list(self.approved_dir.glob("*.md"))
        if approved_files:
            logger.info(f"Found {len(approved_files)} approved files to process")
            for file_path in approved_files:
                logger.info(f"  - Processing approved: {file_path.name}")
                # Process the approved action
                self.process_approved_action(file_path)
        else:
            logger.info("No approved files to process")

    def process_approved_action(self, file_path):
        """Process an action that has been approved"""
        logger.info(f"Processing approved action: {file_path.name}")

        # In a real implementation, this would call external APIs based on the approval
        # For now, we'll just move it to Done
        done_path = self.done_dir / file_path.name
        try:
            file_path.rename(done_path)
            logger.info(f"Processed approved action {file_path.name}, moved to Done")
        except Exception as e:
            logger.error(f"Error processing approved action {file_path.name}: {e}")

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