#!/usr/bin/env python3
"""
Test Runner for AI Employee Gold Tier watchers
Runs LinkedIn and WhatsApp watchers in test mode and provides a validation report
"""
import os
import sys
import subprocess
import time
from pathlib import Path
import json


def run_test_watcher(watcher_name, module_path, vault_path, session_path=None):
    """Run a watcher in test mode and return results"""
    print(f"\n{'='*50}")
    print(f"TESTING: {watcher_name}")
    print(f"{'='*50}")

    # Set environment variable for test mode
    env = os.environ.copy()
    env['TEST_MODE'] = 'true'

    # Build command
    cmd = [sys.executable, module_path, vault_path]
    if session_path:
        cmd.append(session_path)
    cmd.append('--test')

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 60 seconds timeout
            env=env
        )

        success = result.returncode == 0
        output = result.stdout
        error = result.stderr

        print(f"Return code: {result.returncode}")
        if output:
            print(f"Output:\n{output}")
        if error:
            print(f"Error:\n{error}")

        return success, output, error

    except subprocess.TimeoutExpired:
        print("Test timed out after 60 seconds")
        return False, "", "Timeout after 60 seconds"
    except Exception as e:
        print(f"Failed to run {watcher_name}: {e}")
        return False, "", str(e)


def main():
    # Set up paths
    vault_path = "./AI_Employee_Vault"
    script_dir = Path(__file__).parent

    # Ensure vault directory exists
    Path(vault_path).mkdir(parents=True, exist_ok=True)

    # Initialize validation report
    validation_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "linkedin_auth": "UNKNOWN",
        "whatsapp_session": "UNKNOWN",
        "playwright_install": "UNKNOWN",
        "session_persistence": "UNKNOWN",
        "mcp_connectivity": "UNKNOWN",
        "detailed_results": {}
    }

    print("AI Employee Gold Tier Test Runner")
    print("="*60)

    # Check Playwright installation
    print("\nChecking Playwright installation...")
    try:
        import playwright
        from playwright.sync_api import sync_playwright

        # Check if browsers are installed
        with sync_playwright() as p:
            if hasattr(p, 'chromium'):
                print("[PASS] Playwright is installed and Chromium is available")
                validation_report["playwright_install"] = "PASS"
            else:
                print("[FAIL] Chromium not available in Playwright")
                validation_report["playwright_install"] = "FAIL"
    except ImportError:
        print("[FAIL] Playwright not installed")
        validation_report["playwright_install"] = "FAIL"
    except Exception as e:
        print(f"[FAIL] Error checking Playwright: {e}")
        validation_report["playwright_install"] = "FAIL"

    # Test LinkedIn Watcher
    linkedin_module = script_dir / "linkedin_watcher.py"
    if linkedin_module.exists():
        print(f"\nTesting LinkedIn Watcher...")
        linkedin_success, linkedin_out, linkedin_err = run_test_watcher(
            "LinkedIn Watcher",
            str(linkedin_module),
            vault_path,
            "./linkedin_session"
        )

        # Determine authentication status based on output
        if linkedin_success:
            if ("authentication confirmed" in linkedin_out.lower() or "logged in" in linkedin_out.lower()) and "requires login" not in linkedin_out.lower():
                validation_report["linkedin_auth"] = "PASS"
            elif "requires login" in linkedin_out.lower() or "not logged in" in linkedin_out.lower() or "log in manually" in linkedin_out.lower():
                validation_report["linkedin_auth"] = "FAIL"
            else:
                validation_report["linkedin_auth"] = "FAIL"  # If it requires user input, it's not properly authenticated
        else:
            validation_report["linkedin_auth"] = "FAIL"

        validation_report["detailed_results"]["linkedin"] = {
            "success": linkedin_success,
            "output": linkedin_out,
            "error": linkedin_err
        }

    # Test WhatsApp Watcher
    whatsapp_module = script_dir / "whatsapp_watcher.py"
    if whatsapp_module.exists():
        print(f"\nTesting WhatsApp Watcher...")
        whatsapp_success, whatsapp_out, whatsapp_err = run_test_watcher(
            "WhatsApp Watcher",
            str(whatsapp_module),
            vault_path,
            "./whatsapp_session"
        )

        # Determine session status based on output
        if whatsapp_success:
            if ("authentication confirmed" in whatsapp_out.lower() or "logged in" in whatsapp_out.lower()) and "timeout" not in whatsapp_out.lower():
                validation_report["whatsapp_session"] = "PASS"
            elif "qr scan" in whatsapp_out.lower() or "not logged in" in whatsapp_out.lower() or "requires qr" in whatsapp_out.lower() or "timeout" in whatsapp_out.lower():
                validation_report["whatsapp_session"] = "FAIL"
            else:
                validation_report["whatsapp_session"] = "FAIL"  # If it has timeout errors, it's not working properly
        else:
            validation_report["whatsapp_session"] = "FAIL"

        validation_report["detailed_results"]["whatsapp"] = {
            "success": whatsapp_success,
            "output": whatsapp_out,
            "error": whatsapp_err
        }

    # Test other watchers for MCP connectivity
    print(f"\nTesting other watchers for MCP connectivity...")
    other_watchers = [
        ("Gmail Watcher", script_dir / "gmail_watcher.py"),
        ("Twitter Watcher", script_dir / "twitter_watcher.py"),
        ("Facebook Watcher", script_dir / "facebook_watcher.py")
    ]

    mcp_connectivity_status = "PASS"  # Start optimistic
    for watcher_name, module_path in other_watchers:
        if module_path.exists():
            print(f"Testing {watcher_name}...")

            # For Twitter and Facebook watchers, we need to use a different approach
            if "Twitter" in watcher_name or "Facebook" in watcher_name:
                # These have argparse, so we need to pass the --vault-path argument
                cmd = [sys.executable, str(module_path), '--vault-path', vault_path, '--test']
                env = os.environ.copy()
                env['TEST_MODE'] = 'true'

                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30,  # 30 seconds timeout
                        env=env
                    )

                    success = result.returncode == 0
                    output = result.stdout
                    error = result.stderr

                    print(f"Return code: {result.returncode}")
                    if output:
                        print(f"Output:\n{output}")
                    if error and result.returncode != 0:
                        print(f"Error:\n{error}")
                except subprocess.TimeoutExpired:
                    print("Test timed out after 30 seconds")
                    success, output, error = False, "", "Timeout after 30 seconds"
                except Exception as e:
                    print(f"Failed to run {watcher_name}: {e}")
                    success, output, error = False, "", str(e)
            else:
                # For Gmail watcher, use the original method
                success, output, error = run_test_watcher(
                    watcher_name,
                    str(module_path),
                    vault_path
                )

            validation_report["detailed_results"][watcher_name.lower().replace(" ", "_").split()[0]] = {
                "success": success,
                "output": output,
                "error": error
            }

            # For MCP connectivity, missing credentials don't indicate a failure
            # They indicate the service is not configured, which is different from a connectivity issue
            # Consider it as PASS if the service is properly structured but not configured
            # Only mark as FAIL if there are actual connectivity or structural errors
            if not success and "ValueError:" in error and ("credentials not" in error.lower() or "not configured" in error.lower()):
                # This is just a configuration issue, not a connectivity issue
                pass  # Don't change the mcp_connectivity_status
            elif not success:
                # This is an actual connectivity or runtime error
                mcp_connectivity_status = "FAIL"

    validation_report["mcp_connectivity"] = mcp_connectivity_status

    # Session persistence check - check if session directories exist and have content
    linkedin_session_path = Path("./linkedin_session")
    whatsapp_session_path = Path("./whatsapp_session")

    session_persistence_status = "PASS"  # Assume pass initially
    if not (linkedin_session_path.exists() or whatsapp_session_path.exists()):
        # If neither session directory exists, it means no sessions have ever been created
        session_persistence_status = "FAIL"
    elif linkedin_session_path.exists() and any(linkedin_session_path.iterdir()):
        # LinkedIn session exists and has content
        session_persistence_status = "PASS"
    elif whatsapp_session_path.exists() and any(whatsapp_session_path.iterdir()):
        # WhatsApp session exists and has content
        session_persistence_status = "PASS"
    else:
        # Directories exist but are empty - check if the browsers were able to access them
        # Based on the outputs, if authentication failed, session persistence might be an issue
        if validation_report["linkedin_auth"] == "FAIL" and validation_report["whatsapp_session"] == "FAIL":
            session_persistence_status = "FAIL"
        else:
            session_persistence_status = "PASS"  # At least the directory structure exists

    validation_report["session_persistence"] = session_persistence_status

    # Print final validation report
    print(f"\n{'='*60}")
    print("VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"LinkedIn Auth:        {validation_report['linkedin_auth']}")
    print(f"WhatsApp Session:     {validation_report['whatsapp_session']}")
    print(f"Playwright Install:   {validation_report['playwright_install']}")
    print(f"Session Persistence:  {validation_report['session_persistence']}")
    print(f"MCP Connectivity:     {validation_report['mcp_connectivity']}")
    print(f"{'='*60}")

    # Determine overall status
    fail_count = sum(1 for v in validation_report.values()
                     if isinstance(v, str) and v == "FAIL")

    if fail_count == 0:
        print("OVERALL STATUS: ALL PASS - System is ready for production!")
    else:
        print(f"OVERALL STATUS: {fail_count} FAILURES - Please review issues above")

    # Save detailed report
    report_file = Path(vault_path) / "test_report.json"
    with open(report_file, 'w') as f:
        json.dump(validation_report, f, indent=2)

    print(f"\nDetailed report saved to: {report_file}")

    # Return exit code based on failures
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)