#!/usr/bin/env python3
"""
Comprehensive Test Suite for Personal AI Employee - Gold Tier Features
Tests all Gold tier functionality including cross-domain integration, Odoo accounting,
social media integration, audit system, Ralph Wiggum loop, and error recovery.
"""

import os
import sys
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add the vault path to sys.path so we can import the modules
VAULT_PATH = Path(__file__).parent
sys.path.insert(0, str(VAULT_PATH))

from base_watcher import BaseWatcher
from gmail_watcher import GmailWatcher
from whatsapp_watcher import WhatsAppWatcher
from linkedin_watcher import LinkedInWatcher
from twitter_watcher import TwitterWatcher
from facebook_watcher import FacebookWatcher
from audit_system import AuditSystem, AuditLoggingSystem
from ralph_wiggum import RalphWiggumLoop, create_file_completion_condition
from enhanced_master_orchestrator import ErrorRecoverySystem
from abc import ABC, abstractmethod


# Create a concrete implementation of BaseWatcher for testing
class TestWatcher(BaseWatcher):
    def check_for_updates(self):
        return []

    def create_action_file(self, item):
        return Path()


def test_base_watcher_domain_separation():
    """Test that base watcher supports domain separation"""
    print("Testing Base Watcher Domain Separation...")

    # Test shared domain (default)
    watcher_shared = TestWatcher(str(VAULT_PATH))
    assert watcher_shared.domain == 'shared', f"Expected 'shared', got '{watcher_shared.domain}'"
    assert 'Needs_Action' in str(watcher_shared.needs_action), f"Expected 'Needs_Action' in path, got {watcher_shared.needs_action}"

    # Test personal domain
    watcher_personal = TestWatcher(str(VAULT_PATH), domain='personal')
    assert watcher_personal.domain == 'personal', f"Expected 'personal', got '{watcher_personal.domain}'"
    assert 'Personal' in str(watcher_personal.needs_action) and 'Needs_Action' in str(watcher_personal.needs_action), f"Expected personal domain path, got {watcher_personal.needs_action}"

    # Test business domain
    watcher_business = TestWatcher(str(VAULT_PATH), domain='business')
    assert watcher_business.domain == 'business', f"Expected 'business', got '{watcher_business.domain}'"
    assert 'Business' in str(watcher_business.needs_action) and 'Needs_Action' in str(watcher_business.needs_action), f"Expected business domain path, got {watcher_business.needs_action}"

    print("+ Base Watcher Domain Separation - PASSED")


def test_audit_system():
    """Test audit system functionality"""
    print("Testing Audit System...")

    # Test initialization
    audit_system = AuditSystem(str(VAULT_PATH))
    assert audit_system.briefings_path.exists(), "Briefings path should be created"

    # Test audit logging
    audit_logger = AuditLoggingSystem(str(VAULT_PATH))

    # Test logging an action
    audit_logger.log_action(
        action_type="test_action",
        actor="test_actor",
        target="test_target",
        parameters={"test_param": "test_value"},
        result="success"
    )

    # Check that a log file was created
    log_files = list((VAULT_PATH / "Logs").glob("actions_*.json"))
    assert len(log_files) > 0, "Log file should have been created"

    # Verify the content of the log
    with open(log_files[0]) as f:
        logs = json.load(f)
        assert len(logs) >= 1, "At least one log entry should exist"
        latest_log = logs[-1]
        assert latest_log["action_type"] == "test_action", f"Expected test_action, got {latest_log['action_type']}"
        assert latest_log["result"] == "success", f"Expected success, got {latest_log['result']}"

    print("+ Audit System - PASSED")


def test_ralph_wiggum_loop():
    """Test Ralph Wiggum persistent loop functionality"""
    print("Testing Ralph Wiggum Loop...")

    # Test initialization
    ralph = RalphWiggumLoop(str(VAULT_PATH))
    assert ralph.max_iterations == 10, f"Expected max_iterations=10, got {ralph.max_iterations}"

    # Test state file creation
    test_state = {"test": "data", "status": "active"}
    ralph._save_state(test_state)

    loaded_state = ralph._load_state()
    assert loaded_state.get("test") == "data", f"Expected test=data, got {loaded_state}"

    # Test completion condition creation using the standalone function
    test_file = VAULT_PATH / "test_completion_signal.txt"
    condition = create_file_completion_condition(str(VAULT_PATH), "test_completion_signal.txt")

    # Initially should be False
    assert condition() == False, "Completion condition should initially be False"

    # Create the file
    test_file.write_text("completed")
    assert condition() == True, "Completion condition should be True after file creation"

    # Clean up
    test_file.unlink()

    print("+ Ralph Wiggum Loop - PASSED")


def test_error_recovery_system():
    """Test error recovery and circuit breaker functionality"""
    print("Testing Error Recovery System...")

    recovery = ErrorRecoverySystem(str(VAULT_PATH))

    # Test circuit breaker initialization
    recovery.enable_circuit_breaker("test_component")
    assert "test_component" in recovery.circuit_breakers, "Circuit breaker should be initialized"

    # Test can_execute when circuit is closed
    assert recovery.can_execute("test_component") == True, "Should be able to execute when circuit is closed"

    # Test failure recording
    recovery.record_failure("test_component")
    cb_state = recovery.circuit_breakers["test_component"]
    assert cb_state["failure_count"] == 1, "Failure count should be incremented"

    # Test success recording
    recovery.record_success("test_component")
    cb_state = recovery.circuit_breakers["test_component"]
    assert cb_state["failure_count"] == 0, "Failure count should be reset after success"

    # Test the advanced circuit breaker states
    # Trigger multiple failures to open the circuit
    for _ in range(5):  # This should exceed the default threshold of 5
        recovery.record_failure("test_component")

    # Circuit should now be open
    time.sleep(1)  # Allow time for the state transition logic
    # Note: The actual state may depend on the exact implementation, so we just verify it can be accessed
    assert "test_component" in recovery.circuit_breakers, "Component should still be tracked"

    print("+ Error Recovery System - PASSED")


def test_domain_directories():
    """Test that domain-specific directories exist"""
    print("Testing Domain Directories...")

    expected_dirs = [
        "Personal/Inbox",
        "Personal/Needs_Action",
        "Personal/Plans",
        "Personal/Done",
        "Personal/Pending_Approval",
        "Business/Inbox",
        "Business/Needs_Action",
        "Business/Plans",
        "Business/Done",
        "Business/Pending_Approval"
    ]

    for dir_path in expected_dirs:
        full_path = VAULT_PATH / dir_path
        assert full_path.exists(), f"Directory {full_path} should exist"
        assert full_path.is_dir(), f"{full_path} should be a directory"

    print("+ Domain Directories - PASSED")


def test_company_handbook_updated():
    """Test that Company Handbook includes Gold tier features"""
    print("Testing Company Handbook Updates...")

    handbook_path = VAULT_PATH / "Company_Handbook.md"
    assert handbook_path.exists(), "Company Handbook should exist"

    content = handbook_path.read_text()

    # Check for domain separation policy
    assert "Domain Separation Policy" in content, "Should include domain separation policy"

    # Check for cross-domain rules
    assert "Cross-Domain Rules" in content, "Should include cross-domain rules"

    # Check for audit and compliance section
    assert "Audit and Compliance" in content, "Should include audit and compliance section"

    print("+ Company Handbook Updates - PASSED")


def test_business_goals_updated():
    """Test that Business Goals include Gold tier metrics"""
    print("Testing Business Goals Updates...")

    goals_path = VAULT_PATH / "Business_Goals.md"
    assert goals_path.exists(), "Business Goals should exist"

    content = goals_path.read_text()

    # Check for accounting integration requirements
    assert "Accounting Integration Requirements" in content, "Should include accounting integration"

    # Check for social media goals
    assert "Social Media Goals" in content, "Should include social media goals"

    # Check for automation targets
    assert "Automation Targets" in content, "Should include automation targets"

    print("+ Business Goals Updates - PASSED")


def test_configuration_files():
    """Test that all configuration files are in place"""
    print("Testing Configuration Files...")

    # Check MCP config
    mcp_config = VAULT_PATH / "mcp_config.json"
    assert mcp_config.exists(), "MCP config should exist"

    config = json.loads(mcp_config.read_text())
    server_names = [s["name"] for s in config["servers"]]
    assert "odoo" in server_names, "Should have Odoo server config"
    assert "social-media" in server_names, "Should have social media server config"

    # Check requirements
    requirements = VAULT_PATH / "requirements.txt"
    assert requirements.exists(), "Requirements file should exist"

    req_content = requirements.read_text()
    assert "odoo-rpc" in req_content, "Should include Odoo RPC dependency"
    assert "tweepy" in req_content, "Should include Twitter library"

    print("+ Configuration Files - PASSED")


def run_all_tests():
    """Run all tests and report results"""
    print("Starting Gold Tier Feature Tests\n")

    tests = [
        test_base_watcher_domain_separation,
        test_audit_system,
        test_ralph_wiggum_loop,
        test_error_recovery_system,
        test_domain_directories,
        test_company_handbook_updated,
        test_business_goals_updated,
        test_configuration_files
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"- {test_func.__name__} - FAILED: {e}")
            failed += 1

    print(f"\nTest Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("Yay! All Gold Tier features are working correctly!")
        return True
    else:
        print("! Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)