#!/usr/bin/env python3
"""
Test script to verify Silver Tier functionality
"""

import os
import sys
import time
from pathlib import Path
import json


def test_silver_tier_components():
    """Test that all Silver Tier components are properly implemented"""
    vault_path = Path("./AI_Employee_Vault")

    print("Testing Silver Tier Implementation...")
    print(f"Vault path: {vault_path.absolute()}")
    print()

    # Test 1: Check all required files exist
    required_files = [
        'gmail_watcher.py',
        'whatsapp_watcher.py',
        'linkedin_watcher.py',
        'enhanced_mcp_server.js',
        'scheduler.py',
        'master_orchestrator.py',
        'SILVER_TIER_STATUS.md',
        'SILVER_TIER_PLAN.md'
    ]

    print("Test 1: Required Silver Tier files")
    all_files_exist = True
    for file in required_files:
        file_path = vault_path / file
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file}")
        if not exists:
            all_files_exist = False

    print()

    # Test 2: Check all required directories exist
    required_dirs = [
        'Plans',
        'Business_Reports',
        'Social_Posts'
    ]

    print("Test 2: Required Silver Tier directories")
    all_dirs_exist = True
    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        exists = dir_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_name}/")
        if not exists:
            all_dirs_exist = False

    print()

    # Test 3: Check updated agent skills
    print("Test 3: Updated agent skills documentation")
    agent_skills_path = vault_path / 'agent_skills.md'
    if agent_skills_path.exists():
        with open(agent_skills_path, 'r') as f:
            content = f.read()

        # Check for Silver Tier skills
        silver_skills = [
            'send_email',
            'post_linkedin',
            'schedule_task',
            'process_whatsapp',
            'process_gmail',
            'process_linkedin',
            'request_approval'
        ]

        all_skills_present = True
        for skill in silver_skills:
            present = skill in content
            status = "✅" if present else "❌"
            print(f"  {status} {skill}")
            if not present:
                all_skills_present = False
    else:
        print("  ❌ agent_skills.md not found")
        all_skills_present = False

    print()

    # Test 4: Check orchestrator has enhanced functionality
    print("Test 4: Enhanced orchestrator functionality")
    orchestrator_path = vault_path / 'orchestrator.py'
    if orchestrator_path.exists():
        with open(orchestrator_path, 'r') as f:
            content = f.read()

        orchestrator_features = [
            'generate_plan_content',
            'requires_approval',
            'execute_plan',
            'monitor_approved_actions',
            'Plans',
            'Pending_Approval'
        ]

        all_features_present = True
        for feature in orchestrator_features:
            present = feature in content
            status = "✅" if present else "❌"
            print(f"  {status} {feature}")
            if not present:
                all_features_present = False
    else:
        print("  ❌ orchestrator.py not found")
        all_features_present = False

    print()

    # Test 5: Check that README has been updated
    print("Test 5: Updated README")
    readme_path = vault_path / 'README.md'
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            content = f.read()

        readme_contains = [
            'Silver Tier',
            'Multiple Watcher Scripts',
            'Claude Reasoning Loop',
            'Human-in-the-Loop Approval Workflow',
            'LinkedIn Business Updates'
        ]

        all_readme_present = True
        for item in readme_contains:
            present = item in content
            status = "✅" if present else "❌"
            print(f"  {status} '{item}' mentioned")
            if not present:
                all_readme_present = False
    else:
        print("  ❌ README.md not found")
        all_readme_present = False

    print()

    # Test 6: Check requirements.txt has new dependencies
    print("Test 6: Updated dependencies")
    requirements_path = vault_path / 'requirements.txt'
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            content = f.read()

        dependencies = [
            'schedule==',
            'google-api-python-client',
            'playwright'
        ]

        all_deps_present = True
        for dep in dependencies:
            present = dep in content
            status = "✅" if present else "❌"
            print(f"  {status} {dep}")
            if not present:
                all_deps_present = False
    else:
        print("  ❌ requirements.txt not found")
        all_deps_present = False

    print()

    # Summary
    print("Silver Tier Implementation Summary:")
    print(f"  Files: {'✅' if all_files_exist else '❌'}")
    print(f"  Directories: {'✅' if all_dirs_exist else '❌'}")
    print(f"  Agent Skills: {'✅' if all_skills_present else '❌'}")
    print(f"  Orchestrator: {'✅' if all_features_present else '❌'}")
    print(f"  README: {'✅' if all_readme_present else '❌'}")
    print(f"  Dependencies: {'✅' if all_deps_present else '❌'}")

    overall_success = (
        all_files_exist and
        all_dirs_exist and
        all_skills_present and
        all_features_present and
        all_readme_present and
        all_deps_present
    )

    print()
    if overall_success:
        print("🎉 Silver Tier implementation verification: SUCCESS!")
        print("All components are properly implemented and documented.")
    else:
        print("❌ Silver Tier implementation verification: INCOMPLETE")
        print("Some components are missing or not properly implemented.")

    return overall_success


if __name__ == "__main__":
    success = test_silver_tier_components()
    sys.exit(0 if success else 1)