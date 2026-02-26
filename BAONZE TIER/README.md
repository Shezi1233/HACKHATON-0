# AI Employee - Bronze Tier Implementation

This project implements the Bronze Tier requirements for the Personal AI Employee Hackathon.

## Components

### 1. Obsidian Vault Structure
- `Dashboard.md` - Real-time summary of business/personal activities
- `Company_Handbook.md` - Rules of engagement for the AI Employee
- `Business_Goals.md` - Business objectives and metrics
- Folder structure: `/Inbox`, `/Needs_Action`, `/Done`, `/Logs`, `/Pending_Approval`, `/Approved`, `/Rejected`

### 2. File System Watcher
- Monitors the `/Inbox` folder for new files
- Creates action files in `/Needs_Action` when new items are detected
- Handles both markdown and non-markdown files

### 3. Orchestrator
- Manages the monitoring process
- Processes files in `/Needs_Action` folder
- Moves processed files to `/Done` folder

### 4. Agent Skills Framework
- Documents the intended agent skills
- Follows the requirement that "All AI functionality should be implemented as Agent Skills"

## Setup Instructions

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the filesystem watcher:
   ```
   python filesystem_watcher.py
   ```

3. Run the orchestrator:
   ```
   python orchestrator.py
   ```

## How to Test

1. Place a file in the `Inbox` folder
2. The filesystem watcher should detect it and create an action file in `Needs_Action`
3. The orchestrator should move the file to the `Done` folder after processing

## Architecture

This implementation follows the architecture described in the hackathon document:
- **Perception**: Filesystem watcher monitors for changes
- **Reasoning**: Claude Code processes the files (simulated in this basic implementation)
- **Action**: Files are moved between folders based on processing
- **Persistence**: The Ralph Wiggum loop concept is implemented in the orchestrator

## Next Steps for Higher Tiers

- Silver Tier: Add Gmail and WhatsApp watchers, MCP servers
- Gold Tier: Add accounting system integration, business audit features
- Platinum Tier: Add cloud deployment capabilities