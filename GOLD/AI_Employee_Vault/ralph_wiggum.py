"""
Ralph Wiggum Loop Implementation for Claude Code
Provides persistent task completion loops to ensure tasks are completed before Claude exits
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Callable, Optional


class RalphWiggumLoop:
    """
    Implements the Ralph Wiggum persistent loop pattern to keep Claude working
    until a task is complete, preventing premature exits.
    """

    def __init__(self, vault_path: str, max_iterations: int = 10,
                 iteration_delay: int = 5, completion_check_interval: int = 30):
        """
        Initialize the Ralph Wiggum loop

        Args:
            vault_path: Path to the Obsidian vault
            max_iterations: Maximum number of iterations before giving up
            iteration_delay: Delay in seconds between Claude processing attempts
            completion_check_interval: How often to check for completion (seconds)
        """
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.iteration_delay = iteration_delay
        self.completion_check_interval = completion_check_interval
        self.state_file = self.vault_path / '.ralph_wiggum_state.json'

    def run_task_with_persistence(self, task_description: str,
                                  completion_condition: Callable[[], bool],
                                  on_iteration_start: Optional[Callable[[int], None]] = None,
                                  on_completion: Optional[Callable[[], None]] = None,
                                  on_max_iterations_reached: Optional[Callable[[], None]] = None) -> bool:
        """
        Run a task with persistent completion

        Args:
            task_description: Description of the task to be performed
            completion_condition: Function that returns True when task is complete
            on_iteration_start: Callback called at start of each iteration
            on_completion: Callback called when task is completed
            on_max_iterations_reached: Callback when max iterations reached without completion

        Returns:
            True if task completed, False if max iterations reached
        """
        iteration = 0

        # Save initial state
        self._save_state({
            'task_description': task_description,
            'start_time': time.time(),
            'current_iteration': iteration,
            'status': 'active'
        })

        print(f"Starting Ralph Wiggum loop for task: {task_description}")
        print(f"Max iterations: {self.max_iterations}")

        while iteration < self.max_iterations:
            iteration += 1

            if on_iteration_start:
                on_iteration_start(iteration)

            print(f"Iteration {iteration}: Waiting for Claude to process task...")

            # Check if the task is complete
            if completion_condition():
                if on_completion:
                    on_completion()

                final_state = {
                    'task_description': task_description,
                    'start_time': self._load_state().get('start_time'),
                    'end_time': time.time(),
                    'iterations_taken': iteration,
                    'status': 'completed'
                }
                self._save_state(final_state)

                print(f"Task completed after {iteration} iteration(s)!")
                return True

            # Update state
            current_state = self._load_state()
            current_state['current_iteration'] = iteration
            self._save_state(current_state)

            # Wait for Claude to process
            print(f"Task not completed yet. Waiting {self.iteration_delay} seconds before next check...")
            time.sleep(self.iteration_delay)

        # Max iterations reached without completion
        if on_max_iterations_reached:
            on_max_iterations_reached()

        final_state = {
            'task_description': task_description,
            'start_time': self._load_state().get('start_time'),
            'end_time': time.time(),
            'iterations_taken': iteration,
            'status': 'max_iterations_reached'
        }
        self._save_state(final_state)

        print(f"Max iterations ({self.max_iterations}) reached without task completion.")
        return False

    def _save_state(self, state: Dict[str, Any]):
        """Save the current state to the state file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving Ralph Wiggum state: {e}")

    def _load_state(self) -> Dict[str, Any]:
        """Load the current state from the state file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading Ralph Wiggum state: {e}")

        return {}

    def is_task_active(self) -> bool:
        """Check if there's an active Ralph Wiggum task"""
        state = self._load_state()
        return state.get('status') == 'active'

    def get_active_task_status(self) -> Dict[str, Any]:
        """Get the status of the active task"""
        return self._load_state()


def create_file_completion_condition(vault_path: str, expected_file_path: str) -> Callable[[], bool]:
    """
    Create a completion condition that checks for the existence of a specific file

    Args:
        vault_path: Path to the Obsidian vault
        expected_file_path: Path to the file that signals completion (relative to vault)

    Returns:
        A function that returns True when the expected file exists
    """
    def condition():
        expected_file = Path(vault_path) / expected_file_path
        return expected_file.exists()

    return condition


def create_file_moved_completion_condition(vault_path: str, source_folder: str,
                                        target_folder: str, file_pattern: str) -> Callable[[], bool]:
    """
    Create a completion condition that checks if files matching a pattern
    have been moved from source folder to target folder

    Args:
        vault_path: Path to the Obsidian vault
        source_folder: Source folder to check (relative to vault)
        target_folder: Target folder to check (relative to vault)
        file_pattern: Pattern to match files (e.g., 'NEEDS_ACTION_*.md')

    Returns:
        A function that returns True when matching files exist in target folder
    """
    def condition():
        source_path = Path(vault_path) / source_folder
        target_path = Path(vault_path) / target_folder

        # Check if any files with the pattern exist in the target folder
        if target_path.exists():
            for file in target_path.glob(file_pattern):
                return True

        return False

    return condition


def ralph_wiggum_decorator(max_iterations: int = 10, iteration_delay: int = 5):
    """
    Decorator to add Ralph Wiggum persistence to a function

    Args:
        max_iterations: Maximum number of iterations
        iteration_delay: Delay between iterations in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would integrate with Claude Code's hook system
            # For now, we'll just execute the function
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage and testing functions
def example_usage():
    """Example of how to use the Ralph Wiggum loop"""
    vault_path = Path.cwd()  # Current directory as example

    # Example 1: Wait for a specific file to be created
    print("Example 1: Waiting for a specific file to be created")
    expected_file = "completion_signal.txt"

    ralph = RalphWiggumLoop(vault_path, max_iterations=5, iteration_delay=2)

    def create_completion_file():
        """Simulate what Claude would do to complete the task"""
        time.sleep(3)  # Simulate time for Claude to process
        Path(expected_file).write_text("Task completed!")
        print(f"Created {expected_file}")

    # Start the task that creates the completion file in a separate thread
    import threading
    task_thread = threading.Thread(target=create_completion_file)
    task_thread.start()

    # Run the Ralph Wiggum loop
    condition = create_file_completion_condition(str(vault_path), expected_file)
    completed = ralph.run_task_with_persistence(
        task_description="Wait for file creation",
        completion_condition=condition,
        on_iteration_start=lambda i: print(f"  Starting iteration {i}"),
        on_completion=lambda: print("  Task completed!"),
        on_max_iterations_reached=lambda: print("  Max iterations reached without completion.")
    )

    task_thread.join()  # Clean up

    # Clean up example file
    Path(expected_file).unlink(missing_ok=True)

    print(f"\nExample 1 completed successfully: {completed}")


def setup_ralph_wiggum_config():
    """Create configuration file for Claude Code to enable Ralph Wiggum hooks"""
    config_content = """
# Claude Code Configuration for Ralph Wiggum Persistent Loop
# This configuration enables the Ralph Wiggum pattern for persistent task completion

# Example configuration to be placed in Claude Code config:
#
# {
#   "hooks": {
#     "stop": [
#       {
#         "name": "ralph-wiggum-check",
#         "command": "python3 ralph_wiggum_hook.py"
#       }
#     ]
#   }
# }

# The stop hook would check if a task is still running and prevent Claude from exiting
# until the task is marked as complete in a designated completion file or folder.
"""
    return config_content


def main():
    """Main function for example/testing purposes"""
    print("Ralph Wiggum Loop Implementation")
    print("=" * 35)

    example_usage()


if __name__ == "__main__":
    main()