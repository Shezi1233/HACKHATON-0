@echo off
REM Setup script for Gold Tier Personal AI Employee

echo ===========================================
echo Personal AI Employee - Gold Tier Setup
echo ===========================================

set VAULT_PATH=%1
if "%VAULT_PATH%"=="" set VAULT_PATH=.

if not exist "%VAULT_PATH%" (
    echo Error: Vault path %VAULT_PATH% does not exist
    exit /b 1
)

echo Using vault path: %VAULT_PATH%

REM Create necessary directories if they don't exist
echo Creating directory structure...
mkdir "%VAULT_PATH%\Personal\Inbox" 2>nul
mkdir "%VAULT_PATH%\Personal\Needs_Action" 2>nul
mkdir "%VAULT_PATH%\Personal\Plans" 2>nul
mkdir "%VAULT_PATH%\Personal\Done" 2>nul
mkdir "%VAULT_PATH%\Personal\Pending_Approval" 2>nul
mkdir "%VAULT_PATH%\Business\Inbox" 2>nul
mkdir "%VAULT_PATH%\Business\Needs_Action" 2>nul
mkdir "%VAULT_PATH%\Business\Plans" 2>nul
mkdir "%VAULT_PATH%\Business\Done" 2>nul
mkdir "%VAULT_PATH%\Business\Pending_Approval" 2>nul
mkdir "%VAULT_PATH%\Accounting" 2>nul
mkdir "%VAULT_PATH%\Business_Reports\Briefings" 2>nul
mkdir "%VAULT_PATH%\Social_Posts" 2>nul
mkdir "%VAULT_PATH%\mcp_servers" 2>nul

echo Directory structure created.

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r "%VAULT_PATH%\requirements.txt"

REM Setup Playwright browsers for web automation
echo Setting up Playwright browsers...
python -m playwright install chromium

echo ===========================================
echo Setup Complete!
echo ===========================================
echo.
echo Next steps:
echo 1. Configure your environment variables in a .env file:
echo    - Odoo credentials
echo    - Social media API tokens
echo    - Email credentials
echo.
echo 2. Start the enhanced orchestrator:
echo    python enhanced_master_orchestrator.py --vault-path %VAULT_PATH%
echo.
echo 3. Start MCP servers manually if needed:
echo    node mcp_servers/odoo_mcp_server.js
echo    node mcp_servers/social_media_mcp_server.js
echo.
echo Your Gold Tier Personal AI Employee is ready for configuration!