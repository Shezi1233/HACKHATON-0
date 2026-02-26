# AI Employee Vault - Silver Tier

This repository contains the implementation of the Silver Tier of the Personal AI Employee Hackathon project. The AI Employee acts as a digital full-time equivalent, managing personal and business affairs using Claude Code as the reasoning engine and Obsidian as the management dashboard.

## Silver Tier Implementation

The Silver Tier includes all Bronze Tier features plus:

- **Multiple Watcher Scripts**: Gmail, WhatsApp, and LinkedIn monitoring in addition to file system monitoring
- **Claude Reasoning Loop**: Automatic Plan.md file generation with structured task breakdown
- **Human-in-the-Loop Approval Workflow**: Approval system for sensitive actions with Pending_Approval, Approved, and Rejected folders
- **LinkedIn Business Updates**: Automated posting and monitoring capabilities
- **Scheduling System**: Daily, weekly, and monthly business updates including the "Monday Morning CEO Briefing"
- **Enhanced MCP Server**: Extended capabilities for email, LinkedIn, and task scheduling
- **Master Orchestrator**: Centralized management of all components

## Features

### Multi-Source Monitoring
- File system watcher for dropped files
- Gmail watcher for important email notifications
- WhatsApp watcher for urgent message detection
- LinkedIn watcher for business opportunities

### Intelligent Processing
- Claude Code reasoning loops that create structured plan files
- Context-aware task analysis and step breakdown
- Automatic approval requirement detection
- Dashboard updates with real-time information

### Business Intelligence
- Daily business updates
- Weekly "Monday Morning CEO Briefing" with revenue and bottleneck analysis
- Monthly business reviews with strategic insights
- Proactive business suggestions and cost optimization alerts

### Social Media Integration
- Automated LinkedIn post generation
- Approval workflow for social media content
- Hashtag and content suggestions

### Security & Privacy
- Human-in-the-loop approval for sensitive actions
- Clear approval boundaries defined in Company_Handbook.md
- Comprehensive audit logging
- Local-first architecture with privacy-focused design

## Architecture

The system follows the architecture outlined in the hackathon document:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONAL AI EMPLOYEE                         │
│                      SYSTEM ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SOURCES                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│     Gmail       │    WhatsApp     │     LinkedIn    │  Files   │
└────────┬────────┴────────┬────────┴─────────┬────────┴────┬─────┘
         │                 │                  │             │
         ▼                 ▼                  ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────┐ │
│  │ Gmail Watcher│ │WhatsApp Watch│ │LinkedIn Watch│ │File Watch│ │
│  │  (Python)    │ │ (Playwright) │ │ (Playwright) │ │ (Python)│ │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └─────┬───┘ │
└─────────┼────────────────┼────────────────┼───────────────┼─────┘
          │                │                │               │
          ▼                ▼                ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Local)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ /Inbox/        │ /Needs_Action/  │ /Plans/  │ /Done/    │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ /Pending_Approval/ │ /Approved/ │ /Rejected/ │ /Logs/   │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Dashboard.md    │ Company_Handbook.md │ Business_Goals.md│  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      CLAUDE CODE                          │ │
│  │   Read → Think → Plan → Write → Request Approval          │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │
              ┌──────────────────┴───────────────────┐
              ▼                                      ▼
┌────────────────────────────┐    ┌────────────────────────────────┐
│    HUMAN-IN-THE-LOOP       │    │         ACTION LAYER           │
│  ┌──────────────────────┐  │    │  ┌─────────────────────────┐   │
│  │ Review Approval Files│──┼───▶│  │    MCP SERVERS          │   │
│  │ Move to /Approved    │  │    │  │  ┌──────┐ ┌──────────┐  │   │
│  └──────────────────────┘  │    │  │  │Email │ │ LinkedIn │  │   │
│                            │    │  │  │ MCP  │ │   MCP    │  │   │
│  ┌──────────────────────┐  │    │  │  └──┬───┘ └────┬─────┘  │   │
│  │ Process Approved     │──┼───▶│  │     │          │        │   │
│  │ Actions              │  │    │  └─────┼──────────┼────────┘   │
│  └──────────────────────┘  │    └────────┼──────────┼────────────┘
└────────────────────────────┘             │          │
                                           │          │
                                           ▼          ▼
                                  ┌────────────────────────────────┐
                                  │     EXTERNAL ACTIONS           │
                                  │  Send Email │ Post LinkedIn    │
                                  │  Monitor Accounts             │
                                  └────────────────────────────────┘
```

## Setup and Installation

1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers for WhatsApp and LinkedIn monitoring:
   ```bash
   playwright install chromium
   ```
4. Set up Gmail API credentials if using Gmail watcher (optional):
   ```bash
   export GMAIL_CREDENTIALS_PATH=/path/to/your/gmail_credentials.json
   ```

## Usage

To run the complete AI Employee system:

```bash
python master_orchestrator.py
```

This will start all components:
- File system watcher
- Gmail watcher (if credentials available)
- WhatsApp watcher (if Playwright installed)
- LinkedIn watcher (if Playwright installed)
- Claude reasoning orchestrator
- Approval workflow processor
- Business scheduler

## Testing

1. Place test files in the `Inbox` folder to trigger the reasoning loop
2. Monitor the `Needs_Action`, `Plans`, and `Pending_Approval` folders
3. Move files to `Approved` to process approved actions
4. Check the `Dashboard.md` for updates
5. Review generated business reports in the `Business_Reports` folder

## Project Structure

- `Dashboard.md` - Real-time summary dashboard
- `Company_Handbook.md` - Rules of engagement and business policies
- `Business_Goals.md` - Business objectives and metrics
- `Inbox/` - Incoming items for processing
- `Needs_Action/` - Items requiring processing
- `Plans/` - Generated structured plans
- `Pending_Approval/` - Items requiring human approval
- `Approved/` - Items approved for action
- `Rejected/` - Items rejected
- `Done/` - Processed items
- `Business_Reports/` - Daily, weekly, and monthly reports
- `Social_Posts/` - Generated social media content

## Components

- `master_orchestrator.py` - Centralized management of all components
- `orchestrator.py` - Claude reasoning and plan execution
- `gmail_watcher.py` - Gmail monitoring
- `whatsapp_watcher.py` - WhatsApp monitoring
- `linkedin_watcher.py` - LinkedIn monitoring
- `scheduler.py` - Business update scheduling
- `enhanced_mcp_server.js` - MCP server for external actions
- `agent_skills.md` - Documentation of available agent skills

## Security

- All sensitive data is kept local in the Obsidian vault
- Human approval required for sensitive actions
- Proper credential handling with environment variables
- Audit logging for all actions