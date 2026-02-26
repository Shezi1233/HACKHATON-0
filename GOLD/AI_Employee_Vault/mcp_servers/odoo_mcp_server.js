#!/usr/bin/env node

// Odoo MCP Server for Accounting Integration
// Implements MCP v1.0 protocol for integration with Claude Code

import { createServer } from '@modelcontextprotocol/server';
import axios from 'axios';
import dotenv from 'dotenv';
import { createReadStream } from 'fs';

dotenv.config();

const odooConfig = {
  url: process.env.ODOO_URL || 'http://localhost:8069',
  db: process.env.ODOO_DB || 'your_database',
  username: process.env.ODOO_USERNAME || 'admin',
  password: process.env.ODOO_PASSWORD || 'admin',
  version: process.env.ODOO_VERSION || '19.0'
};

let sessionId = null;
let uid = null;

// Authenticate and get session
async function authenticate() {
  try {
    const loginResponse = await axios.post(`${odooConfig.url}/web/session/authenticate`, {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        db: odooConfig.db,
        login: odooConfig.username,
        password: odooConfig.password
      }
    });

    if (loginResponse.data.result && loginResponse.data.result.uid) {
      uid = loginResponse.data.result.uid;
      sessionId = loginResponse.data.result.session_id || null;
      return uid;
    }

    throw new Error('Authentication failed');
  } catch (error) {
    console.error('Odoo Authentication Error:', error);
    throw error;
  }
}

// Helper function to make JSON-RPC requests to Odoo using the modern /jsonrpc endpoint
async function odooRPC(model, method, args = [], kwargs = {}) {
  try {
    // Authenticate if not already done
    if (!uid) {
      await authenticate();
    }

    // Use the authenticated uid from session
    const response = await axios.post(`${odooConfig.url}/jsonrpc`, {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'object',
        method: 'execute_kw',
        args: [odooConfig.db, uid, odooConfig.password, model, method, args, kwargs]
      }
    }, {
      headers: sessionId ? { 'X-Openerp-Session-Id': sessionId } : {}
    });

    if (response.data.error) {
      throw new Error(`Odoo Error: ${response.data.error.message}`);
    }

    return response.data.result;
  } catch (error) {
    console.error('Odoo RPC Error:', error);
    throw error;
  }
}

// Authenticate and get session
async function authenticate() {
  try {
    const loginResponse = await axios.post(`${odooConfig.url}/web/session/authenticate`, {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        db: odooConfig.db,
        login: odooConfig.username,
        password: odooConfig.password
      }
    });

    if (loginResponse.data.result && loginResponse.data.result.uid) {
      odooConfig.uid = loginResponse.data.result.uid;
      return true;
    }

    throw new Error('Authentication failed');
  } catch (error) {
    console.error('Odoo Authentication Error:', error);
    throw error;
  }
}

const server = createServer({
  name: 'odoo-mcp-server',
  version: '1.0.0',
  capabilities: [
    {
      type: 'tools',
      tools: [
        {
          name: 'create_customer',
          description: 'Create a new customer in Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              name: { type: 'string', description: 'Customer name' },
              email: { type: 'string', description: 'Customer email' },
              phone: { type: 'string', description: 'Customer phone' },
              street: { type: 'string', description: 'Customer street address' },
              city: { type: 'string', description: 'Customer city' },
              state: { type: 'string', description: 'Customer state/province' },
              zip: { type: 'string', description: 'Customer zip code' },
              country: { type: 'string', description: 'Customer country' }
            },
            required: ['name']
          }
        },
        {
          name: 'create_invoice',
          description: 'Create a new invoice in Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              partner_id: { type: 'integer', description: 'Customer ID' },
              invoice_date: { type: 'string', description: 'Invoice date (YYYY-MM-DD)' },
              journal_id: { type: 'integer', description: 'Journal ID (default is 1 for Sales)' },
              invoice_line_ids: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    name: { type: 'string', description: 'Line item description' },
                    quantity: { type: 'number', description: 'Quantity' },
                    price_unit: { type: 'number', description: 'Unit price' }
                  },
                  required: ['name', 'quantity', 'price_unit']
                }
              }
            },
            required: ['partner_id', 'invoice_date', 'invoice_line_ids']
          }
        },
        {
          name: 'get_customers',
          description: 'Retrieve list of customers from Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              domain: { type: 'array', description: 'Search domain' },
              limit: { type: 'integer', description: 'Limit results' }
            }
          }
        },
        {
          name: 'get_invoices',
          description: 'Retrieve list of invoices from Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              domain: { type: 'array', description: 'Search domain' },
              limit: { type: 'integer', description: 'Limit results' }
            }
          }
        },
        {
          name: 'get_products',
          description: 'Retrieve list of products from Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              domain: { type: 'array', description: 'Search domain' },
              limit: { type: 'integer', description: 'Limit results' }
            }
          }
        },
        {
          name: 'create_expense',
          description: 'Create a new expense in Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              name: { type: 'string', description: 'Expense name/description' },
              total_amount: { type: 'number', description: 'Total amount' },
              date: { type: 'string', description: 'Expense date (YYYY-MM-DD)' },
              employee_id: { type: 'integer', description: 'Employee ID' },
              product_id: { type: 'integer', description: 'Product ID for expense category' }
            },
            required: ['name', 'total_amount', 'date']
          }
        },
        {
          name: 'get_accounting_summary',
          description: 'Get accounting summary for reporting',
          inputSchema: {
            type: 'object',
            properties: {
              start_date: { type: 'string', description: 'Start date (YYYY-MM-DD)' },
              end_date: { type: 'string', description: 'End date (YYYY-MM-DD)' }
            }
          }
        }
      ]
    }
  ]
});

server.handle('tools/call', async ({ toolName, parameters }) => {
  try {
    // Authenticate if not already done
    if (!odooConfig.uid) {
      await authenticate();
    }

    switch (toolName) {
      case 'create_customer':
        const customerData = {
          name: parameters.name,
          email: parameters.email,
          phone: parameters.phone,
          street: parameters.street,
          city: parameters.city,
          state_id: parameters.state,
          zip: parameters.zip,
          country_id: parameters.country
        };
        // Remove undefined values
        Object.keys(customerData).forEach(key => customerData[key] === undefined && delete customerData[key]);

        const customerId = await odooRPC('res.partner', 'create', [customerData]);
        return { success: true, id: customerId, message: `Customer ${parameters.name} created successfully` };

      case 'create_invoice':
        const invoiceData = {
          partner_id: parameters.partner_id,
          invoice_date: parameters.invoice_date,
          move_type: 'out_invoice',
          journal_id: parameters.journal_id || 1
        };

        if (parameters.invoice_line_ids && Array.isArray(parameters.invoice_line_ids)) {
          invoiceData.invoice_line_ids = parameters.invoice_line_ids.map(line => [
            0, 0, {
              name: line.name,
              quantity: line.quantity,
              price_unit: line.price_unit
            }
          ]);
        }

        const invoiceId = await odooRPC('account.move', 'create', [invoiceData]);
        return { success: true, id: invoiceId, message: `Invoice created successfully with ID: ${invoiceId}` };

      case 'get_customers':
        const customerDomain = parameters.domain || [];
        const customerLimit = parameters.limit || 20;
        const customers = await odooRPC('res.partner', 'search_read', [
          customerDomain,
          ['id', 'name', 'email', 'phone', 'street', 'city', 'state_id', 'zip', 'country_id'],
          { limit: customerLimit }
        ]);
        return { success: true, customers };

      case 'get_invoices':
        const invoiceDomain = parameters.domain || [];
        const invoiceLimit = parameters.limit || 20;
        const invoices = await odooRPC('account.move', 'search_read', [
          invoiceDomain,
          ['id', 'name', 'partner_id', 'invoice_date', 'amount_total', 'state'],
          { limit: invoiceLimit }
        ]);
        return { success: true, invoices };

      case 'get_products':
        const productDomain = parameters.domain || [];
        const productLimit = parameters.limit || 20;
        const products = await odooRPC('product.product', 'search_read', [
          productDomain,
          ['id', 'name', 'list_price', 'default_code'],
          { limit: productLimit }
        ]);
        return { success: true, products };

      case 'create_expense':
        // For expenses, we'll create an accounting entry
        const expenseData = {
          name: parameters.name,
          total_amount: parameters.total_amount,
          date: parameters.date,
          employee_id: parameters.employee_id,
          product_id: parameters.product_id
        };
        // Note: This is a simplified example - real Odoo implementation may vary
        // depending on the installed modules (Expense module, etc.)
        return { success: true, message: 'Expense creation would be implemented based on specific Odoo modules installed' };

      case 'get_accounting_summary':
        const startDate = parameters.start_date || new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0]; // Start of year
        const endDate = parameters.end_date || new Date().toISOString().split('T')[0]; // Today

        // Get total revenue from invoices
        const revenueInvoices = await odooRPC('account.move', 'search_read', [
          [['invoice_date', '>=', startDate], ['invoice_date', '<=', endDate], ['state', '=', 'posted']],
          ['amount_total'],
        ]);
        const totalRevenue = revenueInvoices.reduce((sum, inv) => sum + (inv.amount_total || 0), 0);

        // Get total expenses (simplified approach)
        const expenseEntries = await odooRPC('account.move.line', 'search_read', [
          [['date', '>=', startDate], ['date', '<=', endDate], ['account_id.user_type_id.type', '=', 'expense']],
          ['debit']
        ]);
        const totalExpenses = expenseEntries.reduce((sum, line) => sum + (line.debit || 0), 0);

        // Get pending invoices
        const pendingInvoices = await odooRPC('account.move', 'search_read', [
          [['invoice_date', '>=', startDate], ['invoice_date', '<=', endDate], ['state', '=', 'draft']],
          ['amount_total']
        ]);
        const pendingAmount = pendingInvoices.reduce((sum, inv) => sum + (inv.amount_total || 0), 0);

        return {
          success: true,
          summary: {
            period: `${startDate} to ${endDate}`,
            total_revenue: totalRevenue,
            total_expenses: totalExpenses,
            pending_invoices_amount: pendingAmount,
            net_income: totalRevenue - totalExpenses
          }
        };

      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }
  } catch (error) {
    return {
      success: false,
      error: error.message,
      toolName
    };
  }
});

// Start the server
const port = process.env.PORT || 8085;
server.listen({ port })
  .then(() => {
    console.log(`Odoo MCP Server running on port ${port}`);
  })
  .catch((error) => {
    console.error('Failed to start Odoo MCP Server:', error);
  });