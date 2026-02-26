# Agent Skills for AI Employee - Silver Tier

This file documents the agent skills that are implemented for the AI Employee.

## Core Skills

### File Management Skills
- **read_file**: Read content from files in the vault
- **write_file**: Write content to files in the vault
- **move_file**: Move files between vault folders (Inbox, Needs_Action, Done)
- **list_files**: List files in specific vault directories

### Communication Skills
- **process_email**: Process incoming email notifications and take appropriate action
- **generate_reply**: Generate appropriate replies based on context
- **flag_urgent**: Identify and flag urgent communications

### Business Process Skills
- **create_invoice**: Generate invoice documents based on project data
- **update_dashboard**: Update the Dashboard.md with latest information
- **process_approval**: Handle approval requests and move files appropriately
- **create_plan**: Generate structured plan files for complex tasks

### Monitoring Skills
- **watch_folder**: Monitor specified folders for new files
- **detect_changes**: Detect changes in the vault and trigger appropriate responses
- **log_activity**: Log all AI employee activities for audit purposes

### External Action Skills (Silver Tier)
- **send_email**: Send emails using Gmail API via MCP server
- **post_linkedin**: Post business updates on LinkedIn via MCP server
- **schedule_task**: Schedule recurring tasks and reminders
- **process_whatsapp**: Handle WhatsApp messages received via watcher
- **process_gmail**: Process Gmail notifications received via watcher
- **process_linkedin**: Process LinkedIn notifications received via watcher

### Human-in-the-Loop Skills (Silver Tier)
- **request_approval**: Create approval request files for sensitive actions
- **monitor_approvals**: Monitor Pending_Approval folder for human decisions
- **execute_approved**: Execute actions that have been approved by human

## MCP Server Integration

These skills are implemented using Claude Code's Model Context Protocol (MCP) servers:

### Enhanced MCP Server Methods
- **send_email**: Parameters (to, subject, body) → Send an email
- **post_linkedin**: Parameters (content, title, visibility) → Post on LinkedIn
- **create_plan**: Parameters (task, objective, steps, priority) → Create structured plan
- **schedule_task**: Parameters (task, schedule, description) → Schedule recurring tasks

## Implementation Notes

These skills are now fully implemented and operational as part of the Silver Tier functionality.

- File management and monitoring skills from Bronze Tier remain active
- New communication skills for email, WhatsApp, and LinkedIn are now available
- Human-in-the-loop approval workflow is operational
- MCP server integration allows external actions