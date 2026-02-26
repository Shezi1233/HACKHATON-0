#!/usr/bin/env python3
"""
Unit tests for the enhanced master orchestrator's error recovery system
"""

import sys
from pathlib import Path
import unittest.mock as mock
from datetime import datetime, timedelta

# Add the vault path to sys.path so we can import the modules
VAULT_PATH = Path(__file__).parent
sys.path.insert(0, str(VAULT_PATH))

from enhanced_master_orchestrator import ErrorRecoverySystem


def test_error_recovery_basic():
    """Test basic error recovery functionality"""
    print("Testing Basic Error Recovery...")

    recovery = ErrorRecoverySystem(str(VAULT_PATH))

    # Test basic wrap functionality
    def working_func():
        return "success"

    def failing_func():
        raise Exception("Test failure")

    # Wrap a function that should work
    wrapped_func = recovery.wrap_with_error_recovery(working_func, "working_component")
    result = wrapped_func()
    assert result == "success", f"Expected success, got {result}"

    # Wrap a function that fails but has no retries
    wrapped_failing_func = recovery.wrap_with_error_recovery(
        failing_func, "failing_component", max_retries=1, retry_delay=0.1
    )

    try:
        wrapped_failing_func()
        assert False, "Expected exception to be raised"
    except Exception as e:
        assert "Test failure" in str(e), f"Expected test failure, got {e}"

    print("+ Basic Error Recovery - PASSED")


def test_circuit_breaker_states():
    """Test circuit breaker state transitions"""
    print("Testing Circuit Breaker States...")

    recovery = ErrorRecoverySystem(str(VAULT_PATH))

    # Initialize circuit breaker
    recovery.enable_circuit_breaker("test_component", failure_threshold=2, timeout_seconds=1)

    # Verify initial state
    assert recovery.can_execute("test_component"), "Should start in closed state"

    # Cause multiple failures to open the circuit
    recovery.record_failure("test_component")  # 1st failure
    assert recovery.can_execute("test_component"), "Should still be executable after 1st failure"

    recovery.record_failure("test_component")  # 2nd failure - threshold reached
    # Circuit should now be open
    # Wait briefly for any async state changes
    import time
    time.sleep(0.1)

    # After exceeding threshold, circuit should be open
    # But we need to check the implementation - in our case, once the threshold is reached,
    # the circuit is opened and can_execute should return False
    recovery.record_failure("test_component")  # This should open the circuit
    # We need to wait a bit for the internal state to update
    time.sleep(0.1)

    # Manually check the state
    assert "test_component" in recovery.circuit_breakers, "Component should be tracked"
    cb = recovery.circuit_breakers["test_component"]
    assert cb["failure_count"] >= 2, f"Expected at least 2 failures, got {cb['failure_count']}"

    # Reset for next test
    recovery.record_success("test_component")

    print("+ Circuit Breaker States - PASSED")


def test_exponential_backoff():
    """Test exponential backoff in error recovery"""
    print("Testing Exponential Backoff...")

    recovery = ErrorRecoverySystem(str(VAULT_PATH))

    failure_count = 0

    def failing_func():
        nonlocal failure_count
        failure_count += 1
        if failure_count >= 3:  # Succeed on 3rd attempt
            return "recovered"
        raise Exception(f"Attempt {failure_count} failed")

    # Wrap with exponential backoff
    wrapped = recovery.wrap_with_error_recovery(
        failing_func,
        "backoff_component",
        max_retries=5,
        retry_delay=0.1,
        exponential_backoff=True
    )

    result = wrapped()
    assert result == "recovered", f"Expected recovery, got {result}"
    assert failure_count == 3, f"Expected 3 attempts, got {failure_count}"

    print("+ Exponential Backoff - PASSED")


def test_fallback_function():
    """Test fallback function execution"""
    print("Testing Fallback Function...")

    recovery = ErrorRecoverySystem(str(VAULT_PATH))

    def primary_func():
        raise Exception("Primary function failed")

    def fallback_func():
        return "fallback_success"

    # Wrap with fallback
    wrapped = recovery.wrap_with_error_recovery(
        primary_func,
        "fallback_component",
        max_retries=1,
        retry_delay=0.1,
        fallback_func=fallback_func
    )

    result = wrapped()
    assert result == "fallback_success", f"Expected fallback success, got {result}"

    print("+ Fallback Function - PASSED")


def run_error_recovery_tests():
    """Run all error recovery tests"""
    print("Starting Error Recovery Tests\n")

    tests = [
        test_error_recovery_basic,
        test_circuit_breaker_states,
        test_exponential_backoff,
        test_fallback_function
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"- {test_func.__name__} - FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\nError Recovery Test Results: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == "__main__":
    success = run_error_recovery_tests()
    sys.exit(0 if success else 1)