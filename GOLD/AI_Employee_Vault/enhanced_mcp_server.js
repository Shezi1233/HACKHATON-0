#!/usr/bin/env node
/**
 * Enhanced MCP Server for AI Employee Silver Tier
 * This server handles external actions like email sending and LinkedIn posting
 */

const fs = require('fs').promises;
const path = require('path');
const { google } = require('googleapis'); // For Gmail integration
const express = require('express'); // For webhooks and scheduling

// Enhanced MCP server implementation
class EnhancedMCP {
  constructor() {
    this.vaultPath = './AI_Employee_Vault';
    this.gmailService = null;
    this.linkedInService = null;
  }

  async initialize() {
    // Initialize services if credentials are available
    if (this.hasGmailCredentials()) {
      this.gmailService = await this.initializeGmailService();
    }
  }

  hasGmailCredentials() {
    const credPath = process.env.GMAIL_CREDENTIALS_PATH || path.join(this.vaultPath, 'gmail_credentials.json');
    return fs.existsSync(credPath);
  }

  async initializeGmailService() {
    // This would initialize the Gmail service with proper credentials
    // For now, we'll just return a mock service
    console.log('Gmail service initialized (mocked for now)');
    return {
      sendEmail: async (to, subject, body) => {
        console.log(`MOCK: Would send email to ${to} with subject: ${subject}`);
        return { success: true, messageId: 'mock_' + Date.now() };
      }
    };
  }

  async handleRequest(request) {
    const { method, params } = request;

    switch (method) {
      case 'mcp.builtin.list_resource_templates':
        return this.listResourceTemplates();

      case 'mcp.builtin.read_resource':
        return this.readResource(params.uri);

      case 'mcp.builtin.list_resources':
        return this.listResources(params.type);

      // Custom methods for Silver Tier functionality
      case 'send_email':
        return this.sendEmail(params);

      case 'post_linkedin':
        return this.postLinkedIn(params);

      case 'create_plan':
        return this.createPlan(params);

      case 'schedule_task':
        return this.scheduleTask(params);

      default:
        throw new Error(`Unsupported method: ${method}`);
    }
  }

  async listResourceTemplates() {
    return {
      resourceTemplates: [
        {
          type: "file",
          uriTemplate: "file:///{path}",
          description: "File in the AI Employee vault"
        },
        {
          type: "email",
          uriTemplate: "email://send?to={to}&subject={subject}",
          description: "Send an email"
        },
        {
          type: "linkedin_post",
          uriTemplate: "linkedin://post?content={content}",
          description: "Post on LinkedIn"
        }
      ]
    };
  }

  async readResource(uri) {
    // Parse the file URI
    if (uri.startsWith('file://')) {
      const filePath = uri.slice(7); // Remove 'file://'
      const fullPath = path.join(this.vaultPath, filePath);

      try {
        const content = await fs.readFile(fullPath, 'utf8');
        return {
          contents: [{
            uri: uri,
            text: content,
            mimeType: 'text/markdown'
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri,
            text: `Error reading file: ${error.message}`,
            mimeType: 'text/plain'
          }]
        };
      }
    }

    throw new Error(`Unsupported URI: ${uri}`);
  }

  async listResources(type) {
    if (type === 'file') {
      // List files in the vault
      const inboxPath = path.join(this.vaultPath, 'Inbox');
      const needsActionPath = path.join(this.vaultPath, 'Needs_Action');
      const donePath = path.join(this.vaultPath, 'Done');
      const plansPath = path.join(this.vaultPath, 'Plans');
      const pendingApprovalPath = path.join(this.vaultPath, 'Pending_Approval');
      const approvedPath = path.join(this.vaultPath, 'Approved');

      const resources = [];

      // List files in each directory
      for (const [dirName, dirPath] of [
        ['Inbox', inboxPath],
        ['Needs_Action', needsActionPath],
        ['Done', donePath],
        ['Plans', plansPath],
        ['Pending_Approval', pendingApprovalPath],
        ['Approved', approvedPath]
      ]) {
        try {
          const files = await fs.readdir(dirPath);
          for (const file of files) {
            if (file.endsWith('.md')) {
              resources.push({
                uri: `file:///${dirName}/${file}`,
                name: file,
                description: `File in ${dirName} folder`
              });
            }
          }
        } catch (error) {
          // Directory might not exist or be empty
          console.error(`Error reading directory ${dirName}:`, error.message);
        }
      }

      return { resources };
    }

    throw new Error(`Unsupported resource type: ${type}`);
  }

  // Custom methods for Silver Tier functionality
  async sendEmail(params) {
    const { to, subject, body, htmlBody } = params;

    try {
      // In a real implementation, this would send the actual email
      // For now, we'll simulate and log the action
      if (this.gmailService) {
        const result = await this.gmailService.sendEmail(to, subject, body);
        return {
          success: true,
          messageId: result.messageId,
          message: `Email sent to ${to}`
        };
      } else {
        // Mock email sending
        console.log(`MOCK EMAIL SENT:`);
        console.log(`  To: ${to}`);
        console.log(`  Subject: ${subject}`);
        console.log(`  Body: ${body}`);

        return {
          success: true,
          messageId: 'mock_' + Date.now(),
          message: `Mock email sent to ${to}`
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async postLinkedIn(params) {
    const { content, title, visibility = 'PUBLIC' } = params;

    try {
      // In a real implementation, this would post to LinkedIn
      // For now, we'll simulate and log the action
      console.log(`MOCK LINKEDIN POST:`);
      console.log(`  Title: ${title || 'Untitled Post'}`);
      console.log(`  Content: ${content}`);
      console.log(`  Visibility: ${visibility}`);

      // Create a record of the post in the vault
      const postRecord = {
        timestamp: new Date().toISOString(),
        content: content,
        title: title || 'Untitled Post',
        visibility: visibility,
        status: 'mock_posted'
      };

      return {
        success: true,
        postId: 'mock_' + Date.now(),
        message: `Mock LinkedIn post created`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async createPlan(params) {
    const { task, objective, steps, priority = 'medium' } = params;

    try {
      // Create a plan file in the Plans directory
      const planId = Date.now();
      const planFilename = `PLAN_${planId}.md`;
      const planPath = path.join(this.vaultPath, 'Plans', planFilename);

      const planContent = `---
created: ${new Date().toISOString()}
status: pending
priority: ${priority}
---

# Plan: ${objective}

## Task
${task}

## Steps
${steps.map((step, index) => `- [ ] ${step}`).join('\n')}

## Completion Criteria
- [ ] All steps completed
- [ ] Results validated
- [ ] Dashboard updated
`;

      await fs.writeFile(planPath, planContent);

      return {
        success: true,
        planFile: planFilename,
        path: planPath,
        message: `Plan created: ${planFilename}`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async scheduleTask(params) {
    const { task, schedule, description } = params;

    try {
      // In a real implementation, this would integrate with system scheduler
      // For now, we'll just log the scheduled task
      console.log(`TASK SCHEDULED:`);
      console.log(`  Task: ${task}`);
      console.log(`  Schedule: ${schedule}`);
      console.log(`  Description: ${description}`);

      return {
        success: true,
        message: `Task scheduled: ${description}`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
}

// Main MCP server execution
async function main() {
  console.log('Enhanced MCP Server for AI Employee - Silver Tier');
  console.log('Supporting email sending, LinkedIn posting, and task scheduling');

  const mcp = new EnhancedMCP();
  await mcp.initialize();

  // In a real MCP server, you'd listen for requests from Claude Code
  // This is a simplified demonstration of how it would work

  // Example usage of new methods:
  console.log('\nExample MCP Method Calls:');
  console.log('1. send_email - Send emails through Gmail API');
  console.log('2. post_linkedin - Post updates to LinkedIn');
  console.log('3. create_plan - Create structured plan files');
  console.log('4. schedule_task - Schedule recurring tasks');
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = EnhancedMCP;