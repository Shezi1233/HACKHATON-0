# Agent Skills for AI Employee

This file documents the agent skills that will be implemented for the AI Employee.

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

### Monitoring Skills
- **watch_folder**: Monitor specified folders for new files
- **detect_changes**: Detect changes in the vault and trigger appropriate responses
- **log_activity**: Log all AI employee activities for audit purposes

## Implementation Notes

These skills will be implemented using Claude Code's Model Context Protocol (MCP) servers that can interact with the file system and external services as needed.

For the Bronze Tier, the focus will be on file management and basic monitoring capabilities.