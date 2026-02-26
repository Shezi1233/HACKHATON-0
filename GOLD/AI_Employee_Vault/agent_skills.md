# Agent Skills for AI Employee - Gold Tier

## Overview
This document describes the comprehensive agent skills for the AI Employee system at the Gold tier level, including cross-domain integration, accounting, and multi-platform social media capabilities.

## Core File System Operations
- **read_file**: Read content from files in the vault
- **write_file**: Write content to files in the vault
- **move_file**: Move files between vault folders (Inbox, Needs_Action, Done)
- **list_files**: List files in specific vault directories
- **find_files_by_pattern**: Find files matching a specific pattern across the vault
- **update_dashboard**: Update the dashboard with current status
- **create_directory**: Create new directories for organizational purposes

## Communication Skills
- **process_email**: Process incoming email notifications and take appropriate action
- **generate_reply**: Generate appropriate replies based on context
- **flag_urgent**: Identify and flag urgent communications
- **send_email**: Send emails using Gmail API via MCP server
- **process_whatsapp**: Handle WhatsApp messages received via watcher
- **process_gmail**: Process Gmail notifications received via watcher
- **process_linkedin**: Process LinkedIn notifications received via watcher
- **process_twitter**: Process Twitter notifications received via watcher
- **process_facebook**: Process Facebook notifications received via watcher
- **process_instagram**: Process Instagram notifications received via watcher

## Business Process Skills
- **create_invoice**: Generate invoice documents based on project data
- **update_dashboard**: Update the Dashboard.md with latest information
- **process_approval**: Handle approval requests and move files appropriately
- **create_plan**: Generate structured plan files for complex tasks
- **generate_business_report**: Create comprehensive business reports
- **update_business_goals**: Update business goals based on performance
- **create_accounting_entry**: Create accounting entries in integrated system

## Cross-Domain Operations
- **process_personal_task**: Handle personal tasks and activities with appropriate privacy
- **process_business_task**: Handle business tasks and activities with appropriate separation
- **manage_cross_domain_rules**: Apply rules that span personal and business domains
- **maintain_domain_separation**: Ensure proper separation between personal and business data
- **transfer_domain_data**: Safely transfer necessary data between domains when appropriate

## Odoo Accounting Integration Skills
- **create_customer**: Create a new customer in the Odoo system
- **create_invoice**: Create a new invoice in the Odoo system (draft mode with approval required)
- **get_customers**: Retrieve list of customers from Odoo
- **get_invoices**: Retrieve list of invoices from Odoo
- **get_products**: Retrieve list of products from Odoo
- **get_accounting_summary**: Get accounting summary from Odoo for reporting
- **create_expense**: Create a new expense in Odoo (draft mode with approval required)
- **process_odoo_approval**: Process draft-only accounting actions with approval requirement

## Social Media Management Skills
- **post_linkedin**: Post business updates on LinkedIn via MCP server
- **post_to_facebook**: Create a post on Facebook page
- **post_to_instagram**: Create a post on Instagram account
- **post_to_twitter**: Create a tweet on Twitter/X
- **schedule_social_post**: Schedule a social media post for later publication
- **get_social_insights**: Get insights/metrics for social media accounts
- **generate_social_content**: Generate content appropriate for social media
- **apply_brand_guidelines**: Apply brand guidelines when creating content
- **generate_hashtags**: Generate relevant hashtags for social media posts
- **analyze_engagement_metrics**: Analyze engagement metrics for content optimization

## Monitoring Skills
- **watch_folder**: Monitor specified folders for new files
- **detect_changes**: Detect changes in the vault and trigger appropriate responses
- **log_activity**: Log all AI employee activities for audit purposes
- **monitor_personal_domain**: Monitor personal domain activities and files
- **monitor_business_domain**: Monitor business domain activities and files

## Advanced Planning and Scheduling
- **create_plan**: Generate structured plan files for complex tasks
- **schedule_task**: Schedule recurring tasks and reminders
- **generate_weekly_briefing**: Generate the comprehensive Monday morning CEO briefing
- **generate_accounting_audit**: Create periodic accounting audit reports
- **schedule_weekly_briefing**: Schedule the weekly CEO briefing generation
- **schedule_daily_updates**: Schedule daily business updates
- **schedule_social_posts**: Schedule social media content
- **schedule_accounting_reports**: Schedule periodic accounting reports

## Persistent Task Execution (Ralph Wiggum Loop)
- **start_persistent_task**: Begin a task that continues until completion
- **check_task_completion**: Check if a persistent task has been completed
- **create_completion_condition**: Set up conditions that determine task completion
- **manage_task_state**: Manage the state of persistent tasks
- **continue_until_done**: Continue task execution until specific completion criteria are met

## Human-in-the-Loop Skills
- **request_approval**: Create approval request files for sensitive actions
- **monitor_approvals**: Monitor Pending_Approval folder for human decisions
- **execute_approved**: Execute actions that have been approved by human
- **create_approval_request**: Generate structured approval requests with all necessary details
- **update_approval_status**: Update the status of an approval request
- **escalate_complex_approval**: Escalate complex approval requests with additional context

## Audit and Logging Skills
- **log_action**: Log an action performed by the AI Employee
- **generate_audit_report**: Create an audit report for compliance
- **check_compliance**: Check if an action complies with audit requirements
- **create_audit_trail**: Create a complete audit trail for an operation
- **maintain_compliance_logs**: Maintain logs to meet compliance requirements

## Error Recovery and Management Skills
- **retry_operation**: Retry an operation that failed with exponential backoff
- **enable_circuit_breaker**: Enable circuit breaker pattern for a component
- **can_execute_action**: Check if an action can be executed (circuit breaker check)
- **record_failure**: Record a failure for a component
- **record_success**: Record a success for a component, resetting failure count
- **graceful_degradation**: Implement graceful degradation when components fail
- **fallback_operation**: Execute fallback operations when primary fails

## MCP Server Integration

These skills are implemented using Claude Code's Model Context Protocol (MCP) servers:

### Odoo MCP Server Methods
- **create_customer**: Parameters (name, email, phone, address details) → Create customer in Odoo
- **create_invoice**: Parameters (partner_id, invoice_date, invoice_lines) → Create invoice (draft)
- **get_customers**: Parameters (domain, limit) → Retrieve customer list
- **get_invoices**: Parameters (domain, limit) → Retrieve invoice list
- **get_products**: Parameters (domain, limit) → Retrieve product list
- **get_accounting_summary**: Parameters (start_date, end_date) → Get financial summary

### Social Media MCP Server Methods
- **post_to_facebook**: Parameters (message, link, attachments) → Post on Facebook
- **post_to_instagram**: Parameters (caption, media_url, hashtags) → Post on Instagram
- **post_to_twitter**: Parameters (text, media_urls, reply_to_id) → Post on Twitter/X
- **schedule_social_post**: Parameters (platform, content, scheduled_time) → Schedule post
- **get_facebook_insights**: Parameters (metric, period) → Get Facebook metrics
- **get_instagram_insights**: Parameters (metric, period) → Get Instagram metrics
- **get_twitter_insights**: Parameters (start_date, end_date) → Get Twitter metrics

### Enhanced Communication MCP Methods
- **send_email**: Parameters (to, subject, body) → Send an email
- **create_plan**: Parameters (task, objective, steps, priority) → Create structured plan
- **schedule_task**: Parameters (task, schedule, description) → Schedule recurring tasks

## Domain-Specific Folders
The AI Employee manages activities in these domain-specific folders:

### Personal Domain
- `/Personal/Inbox` - Personal communications received
- `/Personal/Needs_Action` - Personal tasks requiring attention
- `/Personal/Plans` - Personal task plans and checklists
- `/Personal/Done` - Completed personal activities
- `/Personal/Pending_Approval` - Personal actions awaiting approval

### Business Domain
- `/Business/Inbox` - Business communications received
- `/Business/Needs_Action` - Business tasks requiring attention
- `/Business/Plans` - Business task plans and checklists
- `/Business/Done` - Completed business activities
- `/Business/Pending_Approval` - Business actions awaiting approval

### Shared Folders
- `/Accounting` - Accounting-related files and reports
- `/Business_Reports` - Generated business reports and briefings
- `/Social_Posts` - Social media content drafts and schedules

## Implementation Notes

These skills are now fully implemented and operational as part of the Gold Tier functionality:

- All Bronze and Silver Tier skills remain active and functional
- Cross-domain capabilities enable proper separation of personal and business activities
- Odoo accounting integration provides comprehensive financial management
- Multi-platform social media capabilities enhance business outreach
- Extended approval workflows maintain security and compliance
- Ralph Wiggum persistent loops ensure task completion
- Comprehensive audit logging maintains compliance
- Error recovery and graceful degradation ensure system reliability
- MCP server integration enables all external actions

## Configuration Requirements
- Social media skills require proper API credentials configured in environment variables
- Odoo skills require Odoo server running and proper credentials configured
- Approval workflows follow the rules defined in Company_Handbook.md
- Audit logs are stored in the /Logs directory and maintained per security policy
- Domain separation rules are enforced as per Company_Handbook.md guidelines