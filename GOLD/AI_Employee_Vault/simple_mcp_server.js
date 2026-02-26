#!/usr/bin/env node
/**
 * Simple MCP Server for AI Employee Bronze Tier
 * This server demonstrates the MCP concept for the Bronze Tier
 */

const fs = require('fs').promises;
const path = require('path');

// Simple MCP server implementation
class SimpleMCP {
  constructor() {
    this.vaultPath = './AI_Employee_Vault';
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

      const resources = [];

      // List files in each directory
      for (const [dirName, dirPath] of [
        ['Inbox', inboxPath],
        ['Needs_Action', needsActionPath],
        ['Done', donePath]
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
}

// Main execution
async function main() {
  console.log('Simple MCP Server for AI Employee - Bronze Tier');
  console.log('This server demonstrates MCP concepts for Claude Code integration');

  // In a real MCP server, you'd listen for requests from Claude Code
  // For Bronze Tier, this serves as a demonstration of how MCP integration works
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = SimpleMCP;