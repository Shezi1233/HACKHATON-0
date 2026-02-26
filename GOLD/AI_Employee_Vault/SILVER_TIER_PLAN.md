# Silver Tier Implementation Plan

## Silver Tier Requirements (from hackathon document)

### All Bronze requirements plus:
1. Two or more Watcher scripts (e.g., Gmail + Whatsapp + LinkedIn)
2. Automatically Post on LinkedIn about business to generate sales
3. Claude reasoning loop that creates Plan.md files
4. One working MCP server for external action (e.g., sending emails)
5. Human-in-the-loop approval workflow for sensitive actions
6. Basic scheduling via cron or Task Scheduler
7. All AI functionality should be implemented as Agent Skills

## Current Bronze Tier Status

✅ **Obsidian vault with Dashboard.md and Company_Handbook.md**
✅ **One working Watcher script (file system monitoring)**
✅ **Claude Code successfully reading from and writing to the vault**
✅ **Basic folder structure: /Inbox, /Needs_Action, /Done**
✅ **All AI functionality should be implemented as Agent Skills**

## Silver Tier Implementation Plan

### 1. Additional Watcher Scripts
- [ ] Implement Gmail Watcher (based on template in hackathon doc)
- [ ] Implement WhatsApp Watcher (using Playwright)
- [ ] Implement LinkedIn Watcher (monitoring for mentions/messages)
- [ ] Update orchestrator to manage multiple watchers

### 2. LinkedIn Posting Capability
- [ ] Create LinkedIn MCP server for posting
- [ ] Implement business update generation logic
- [ ] Add LinkedIn posting agent skills
- [ ] Create scheduling system for regular posts

### 3. Claude Reasoning Loop with Plan.md
- [ ] Modify orchestrator to trigger Claude when files are in Needs_Action
- [ ] Implement Plan.md generation logic
- [ ] Create reasoning templates for different task types
- [ ] Implement completion tracking in Plan.md files

### 4. MCP Server for External Actions
- [ ] Enhance existing MCP server or create new one for email sending
- [ ] Add browser automation capabilities for payment portals
- [ ] Implement proper error handling and response mechanisms

### 5. Human-in-the-Loop Approval Workflow
- [ ] Enhance approval request file format
- [ ] Create better UI for approval management
- [ ] Implement automatic processing of approved items
- [ ] Add notification system for pending approvals

### 6. Scheduling System
- [ ] Implement task scheduling for regular activities
- [ ] Create weekly/monthly report generation
- [ ] Add recurring business activities management

### 7. Enhanced Agent Skills
- [ ] Expand agent skills to cover all new functionality
- [ ] Create specific skills for each new capability
- [ ] Document new agent skills properly

## Implementation Priority
1. **Critical Infrastructure**: Additional watchers and MCP servers
2. **Core Functionality**: Claude reasoning loop and Plan.md generation
3. **Business Value**: LinkedIn posting capability
4. **User Experience**: Approval workflow and scheduling