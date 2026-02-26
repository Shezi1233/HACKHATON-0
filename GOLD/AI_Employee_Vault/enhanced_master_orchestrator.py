"""
Enhanced Master Orchestrator for the Personal AI Employee
Manages all Gold tier components: watchers, MCP servers, audit system, and Ralph Wiggum loops
"""

import os
import sys
import time
import signal
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import timedelta

# Import existing components
from orchestrator import AI_Employee_Orchestrator
from master_orchestrator import MasterOrchestrator as BaseMasterOrchestrator
from gmail_watcher import GmailWatcher
from whatsapp_watcher import WhatsAppWatcher
from linkedin_watcher import LinkedInWatcher
from twitter_watcher import TwitterWatcher
from facebook_watcher import FacebookWatcher
from scheduler import AIEmployeeScheduler
from audit_system import AuditSystem
from ralph_wiggum import RalphWiggumLoop


@dataclass
class ComponentInfo:
    name: str
    status: str
    last_heartbeat: datetime
    process: Any = None


class EnhancedMasterOrchestrator:
    """Enhanced orchestrator that manages all Gold tier components"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.components: Dict[str, ComponentInfo] = {}
        self.active_threads: List[threading.Thread] = []
        self.running = True

        # Initialize audit logging system
        from audit_system import AuditLoggingSystem
        self.audit_logger = AuditLoggingSystem(vault_path)

        # Initialize audit system
        self.audit_system = AuditSystem(vault_path)

        # Initialize business scheduler
        self.scheduler = AIEmployeeScheduler(vault_path)

        # Initialize all watchers
        self._initialize_watchers()

        # Initialize MCP servers tracking
        self.mcp_servers_status = {}

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _initialize_watchers(self):
        """Initialize all watchers for Gold tier"""
        try:
            # Load credentials
            self.gmail_creds_path = os.getenv('GMAIL_CREDENTIALS_PATH',
                                             self.vault_path / 'gmail_credentials.json')

            # Initialize all watchers
            self.watchers = {
                'gmail': GmailWatcher(str(self.vault_path), str(self.gmail_creds_path)),
                'whatsapp': WhatsAppWatcher(str(self.vault_path)),
                'linkedin': LinkedInWatcher(str(self.vault_path)),
                'twitter': TwitterWatcher(str(self.vault_path)),
                'facebook': FacebookWatcher(str(self.vault_path))
            }

            self.logger.info("All watchers initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing watchers: {e}")
            raise

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)

    def start_all_components(self):
        """Start all orchestrator components"""
        self.logger.info("Starting Enhanced Master Orchestrator...")

        # Start all watchers in separate threads
        for name, watcher in self.watchers.items():
            thread = threading.Thread(target=self._run_watcher, args=(name, watcher), daemon=True)
            thread.start()
            self.active_threads.append(thread)
            self.components[name] = ComponentInfo(
                name=name,
                status='running',
                last_heartbeat=datetime.now()
            )
            self.logger.info(f"Started {name} watcher")

        # Start audit system scheduler
        audit_thread = threading.Thread(target=self._run_audit_scheduler, daemon=True)
        audit_thread.start()
        self.active_threads.append(audit_thread)
        self.components['audit_system'] = ComponentInfo(
            name='audit_system',
            status='running',
            last_heartbeat=datetime.now()
        )

        # Start MCP server manager
        mcp_thread = threading.Thread(target=self._run_mcp_manager, daemon=True)
        mcp_thread.start()
        self.active_threads.append(mcp_thread)
        self.components['mcp_manager'] = ComponentInfo(
            name='mcp_manager',
            status='running',
            last_heartbeat=datetime.now()
        )

        # Start Ralph Wiggum loop manager
        ralph_thread = threading.Thread(target=self._run_ralph_manager, daemon=True)
        ralph_thread.start()
        self.active_threads.append(ralph_thread)
        self.components['ralph_manager'] = ComponentInfo(
            name='ralph_manager',
            status='running',
            last_heartbeat=datetime.now()
        )

        # Start the main monitoring loop
        monitor_thread = threading.Thread(target=self._run_monitoring_loop, daemon=True)
        monitor_thread.start()
        self.active_threads.append(monitor_thread)

        self.logger.info("All components started successfully")
        self.audit_logger.log_action(
            action_type="orchestrator_start",
            actor="enhanced_master_orchestrator",
            target="all_components",
            parameters={"vault_path": str(self.vault_path)},
            result="success"
        )

    def _run_watcher(self, name: str, watcher):
        """Run a watcher in a separate thread"""
        try:
            watcher.run()
        except Exception as e:
            self.logger.error(f"Error in {name} watcher: {e}")
            self.components[name].status = 'error'
            self.audit_logger.log_action(
                action_type="watcher_error",
                actor=name,
                target="watcher_process",
                parameters={"error": str(e)},
                result="error"
            )

    def _run_audit_scheduler(self):
        """Run the audit and reporting scheduler"""
        while self.running:
            try:
                # Generate weekly CEO briefing every Monday morning
                now = datetime.now()
                if now.weekday() == 0 and now.hour == 7 and now.minute < 5:  # Monday 7:00-7:04 AM
                    self.logger.info("Generating weekly CEO briefing...")
                    briefing_path = self.audit_system.generate_weekly_ceo_briefing()
                    self.audit_logger.log_action(
                        action_type="weekly_briefing_generated",
                        actor="audit_system",
                        target=briefing_path,
                        parameters={"week": now.isocalendar()[1]},
                        result="success"
                    )

                # Generate daily reports
                if now.hour == 6 and now.minute < 5:  # 6:00-6:04 AM daily
                    self.logger.info("Generating daily report...")
                    # Add daily report generation logic here if needed
                    pass

                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in audit scheduler: {e}")
                time.sleep(60)

    def _run_mcp_manager(self):
        """Manage MCP server health and status"""
        while self.running:
            try:
                # Check MCP server status
                mcp_status = self._check_mcp_servers()
                self.mcp_servers_status.update(mcp_status)

                # Log MCP server status periodically
                self.audit_logger.log_action(
                    action_type="mcp_status_check",
                    actor="mcp_manager",
                    target="mcp_servers",
                    parameters={"status": mcp_status},
                    result="success"
                )

                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                self.logger.error(f"Error in MCP manager: {e}")
                time.sleep(60)

    def _run_ralph_manager(self):
        """Manage Ralph Wiggum persistent loops"""
        while self.running:
            try:
                # Check for pending Ralph Wiggum tasks
                ralph = RalphWiggumLoop(str(self.vault_path))
                if ralph.is_task_active():
                    status = ralph.get_active_task_status()
                    self.logger.info(f"Active Ralph Wiggum task: {status.get('task_description', 'Unknown')}")

                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in Ralph manager: {e}")
                time.sleep(60)

    def _check_mcp_servers(self) -> Dict[str, str]:
        """Check the status of MCP servers"""
        # In a real implementation, this would ping the actual MCP servers
        # For now, we'll return a simulated status
        return {
            'odoo_server': 'running',
            'social_media_server': 'running',
            'email_server': 'running',
            'browser_server': 'running'
        }

    def _run_monitoring_loop(self):
        """Main monitoring loop to check component health"""
        while self.running:
            try:
                # Update component heartbeats
                for name in self.components:
                    self.components[name].last_heartbeat = datetime.now()

                # Check for any issues
                self._check_component_health()

                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)

    def _check_component_health(self):
        """Check if any components have failed"""
        current_time = datetime.now()

        for name, component in self.components.items():
            # Check if heartbeat is older than 2 minutes
            if (current_time - component.last_heartbeat).seconds > 120:
                self.logger.warning(f"{name} may be unresponsive (last heartbeat: {component.last_heartbeat})")
                component.status = 'unresponsive'

    def get_status(self) -> Dict[str, Any]:
        """Get status of all components"""
        status = {
            'orchestrator': {
                'running': self.running,
                'start_time': getattr(self, 'start_time', datetime.now().isoformat()),
                'components': len(self.components)
            },
            'watchers': {name: {
                'status': info.status,
                'last_heartbeat': info.last_heartbeat.isoformat()
            } for name, info in self.components.items() if 'watcher' in name.lower()},
            'mcp_servers': self.mcp_servers_status,
            'active_threads': len(self.active_threads)
        }
        return status

    def shutdown(self):
        """Gracefully shut down all components"""
        self.logger.info("Shutting down Enhanced Master Orchestrator...")
        self.running = False

        # Wait for threads to finish (with timeout)
        for thread in self.active_threads:
            thread.join(timeout=5)

        self.logger.info("All components shut down")
        self.audit_logger.log_action(
            action_type="orchestrator_shutdown",
            actor="enhanced_master_orchestrator",
            target="all_components",
            parameters={"reason": "graceful_shutdown"},
            result="success"
        )

    def run(self):
        """Main run method"""
        self.start_time = datetime.now()
        self.start_all_components()

        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, shutting down...")
            self.shutdown()


class ErrorRecoverySystem:
    """System for error recovery and graceful degradation"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.recovery_attempts = {}
        self.circuit_breakers = {}
        self.health_check_intervals = {}  # Track health check intervals per component
        self.failure_history = {}  # Track failure history for analysis

    def wrap_with_error_recovery(self, func: Callable, component_name: str,
                                max_retries: int = 3, retry_delay: int = 5,
                                exponential_backoff: bool = True,
                                fallback_func: Optional[Callable] = None):
        """Wrap a function with error recovery and retry logic"""
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = retry_delay
            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    self.logger.error(f"Attempt {attempt}/{max_retries} failed for {component_name}: {e}")

                    # Record the failure in history
                    if component_name not in self.failure_history:
                        self.failure_history[component_name] = []
                    self.failure_history[component_name].append({
                        'timestamp': datetime.now().isoformat(),
                        'error': str(e),
                        'attempt': attempt
                    })

                    if attempt < max_retries:
                        # Implement exponential backoff if enabled
                        if exponential_backoff:
                            time.sleep(current_delay)
                            current_delay *= 2  # Double the delay for next attempt
                        else:
                            time.sleep(retry_delay)
                    else:
                        self.logger.error(f"All retries failed for {component_name}")

                        # Try fallback function if provided
                        if fallback_func:
                            self.logger.info(f"Attempting fallback function for {component_name}")
                            try:
                                return fallback_func(*args, **kwargs)
                            except Exception as fallback_error:
                                self.logger.error(f"Fallback function also failed for {component_name}: {fallback_error}")

                        # Log the failure for audit
                        from audit_system import AuditLoggingSystem
                        audit_logger = AuditLoggingSystem(str(self.vault_path))
                        audit_logger.log_action(
                            action_type="component_failure",
                            actor=component_name,
                            target="function_execution",
                            parameters={
                                "error": str(e),
                                "max_retries": max_retries,
                                "total_attempts": attempt,
                                "fallback_used": fallback_func is not None
                            },
                            result="failure"
                        )
                        raise
        return wrapper

    def enable_circuit_breaker(self, component_name: str, failure_threshold: int = 5,
                              timeout_seconds: int = 300, recovery_threshold: int = 1):
        """Enable circuit breaker pattern for a component"""
        self.circuit_breakers[component_name] = {
            'failure_count': 0,
            'failure_threshold': failure_threshold,
            'last_failure_time': None,
            'open_until': None,
            'timeout_seconds': timeout_seconds,
            'recovery_threshold': recovery_threshold,  # How many successes to close the circuit
            'recovery_count': 0,
            'state': 'closed'  # closed, open, half-open
        }

    def can_execute(self, component_name: str) -> bool:
        """Check if a component can execute (circuit breaker check)"""
        if component_name not in self.circuit_breakers:
            return True

        cb = self.circuit_breakers[component_name]

        current_time = datetime.now()

        # If circuit is in open state, check if timeout has passed to enter half-open state
        if cb['state'] == 'open' and current_time >= cb['open_until']:
            cb['state'] = 'half-open'
            self.logger.info(f"Circuit breaker for {component_name} entering half-open state")
            # Reset recovery counter when entering half-open state
            cb['recovery_count'] = 0

        # If in half-open state, allow one request to test recovery
        if cb['state'] == 'half-open':
            return True

        # If in open state, reject all requests
        if cb['state'] == 'open':
            return False

        # Circuit is closed, allow execution
        return True

    def record_failure(self, component_name: str):
        """Record a failure for a component"""
        if component_name not in self.circuit_breakers:
            self.enable_circuit_breaker(component_name)

        cb = self.circuit_breakers[component_name]
        cb['failure_count'] += 1
        cb['last_failure_time'] = datetime.now()

        # Check if we need to open the circuit
        if cb['failure_count'] >= cb['failure_threshold'] and cb['state'] != 'open':
            cb['open_until'] = datetime.now() + timedelta(seconds=cb['timeout_seconds'])
            cb['state'] = 'open'
            self.logger.warning(f"Circuit breaker opened for {component_name}, will reset in {cb['timeout_seconds']} seconds")

        self.logger.warning(f"Recorded failure for {component_name}, current count: {cb['failure_count']}, state: {cb['state']}")

    def record_success(self, component_name: str):
        """Record a success for a component, resetting failure count"""
        if component_name in self.circuit_breakers:
            cb = self.circuit_breakers[component_name]

            # If in half-open state and successful, increment recovery counter
            if cb['state'] == 'half-open':
                cb['recovery_count'] += 1
                if cb['recovery_count'] >= cb['recovery_threshold']:
                    # Fully recover - reset everything
                    cb['state'] = 'closed'
                    cb['failure_count'] = 0
                    cb['recovery_count'] = 0
                    cb['open_until'] = None
                    self.logger.info(f"Circuit breaker for {component_name} closed after successful recovery")
                else:
                    self.logger.info(f"Circuit breaker recovery attempt {cb['recovery_count']}/{cb['recovery_threshold']} for {component_name}")
            else:
                # In normal closed state, just reset failure count
                cb['failure_count'] = 0
                cb['recovery_count'] = 0

    def record_failure(self, component_name: str):
        """Record a failure for a component"""
        if component_name not in self.circuit_breakers:
            self.enable_circuit_breaker(component_name)

        cb = self.circuit_breakers[component_name]
        cb['failure_count'] += 1
        cb['last_failure_time'] = datetime.now()

        self.logger.warning(f"Recorded failure for {component_name}, current count: {cb['failure_count']}")

    def record_success(self, component_name: str):
        """Record a success for a component, resetting failure count"""
        if component_name in self.circuit_breakers:
            cb = self.circuit_breakers[component_name]
            cb['failure_count'] = 0
            cb['open_until'] = None


# Example usage
def main():
    """Main function to run the Enhanced Master Orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced Master Orchestrator for AI Employee')
    parser.add_argument('--vault-path', type=str, required=True,
                       help='Path to the Obsidian vault')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize and run the orchestrator
    orchestrator = EnhancedMasterOrchestrator(vault_path=args.vault_path)

    try:
        orchestrator.run()
    except Exception as e:
        logging.error(f"Orchestrator failed: {e}")
        # Log the failure
        audit_logger = AuditLoggingSystem(args.vault_path)
        audit_logger.log_action(
            action_type="orchestrator_failure",
            actor="enhanced_master_orchestrator",
            target="main_process",
            parameters={"error": str(e)},
            result="failure"
        )
        raise


if __name__ == "__main__":
    main()