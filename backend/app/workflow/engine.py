"""
Step Functions-style Workflow Orchestration Engine.
Executes a sequential pipeline of stateless Lambda-style handlers,
passing JSON between steps, with logging and error handling at each step.
"""

import logging
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from app.database.dynamo_mock import execution_logs_table, workflow_state_table

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


class WorkflowStep:
    """Represents a single step in the workflow pipeline."""

    def __init__(self, name: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]], retries: int = MAX_RETRIES):
        self.name = name
        self.handler = handler
        self.retries = retries


class WorkflowEngine:
    """
    Orchestrates sequential execution of workflow steps.
    Simulates AWS Step Functions behavior:
    - Sequential execution
    - JSON passing between steps
    - Per-step logging
    - Error handling with retry
    """

    def __init__(self, workflow_id: Optional[str] = None):
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.steps: List[WorkflowStep] = []
        self.execution_log: List[Dict[str, Any]] = []

    def add_step(self, name: str, handler: Callable, retries: int = MAX_RETRIES) -> "WorkflowEngine":
        self.steps.append(WorkflowStep(name=name, handler=handler, retries=retries))
        return self

    def _log_step(self, step_name: str, status: str, input_data: Any, output_data: Any,
                  error: Optional[str] = None, duration_ms: float = 0):
        log_entry = {
            "workflow_id": self.workflow_id,
            "step_name": step_name,
            "status": status,
            "input_summary": _summarize(input_data),
            "output_summary": _summarize(output_data),
            "error": error,
            "duration_ms": round(duration_ms, 2),
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }
        self.execution_log.append(log_entry)
        execution_logs_table.put_item(log_entry)

        # Update workflow state in DynamoDB
        workflow_state_table.put_item({
            "workflow_id": self.workflow_id,
            "step_name": step_name,
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

        logger.info("Step [%s] %s (%.1fms)", step_name, status, duration_ms)

    def execute(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run all steps sequentially, passing output of each as input to the next."""
        logger.info("=== Workflow %s starting with %d steps ===", self.workflow_id, len(self.steps))

        current_input = initial_input
        results = {}

        for i, step in enumerate(self.steps):
            step_start = datetime.now(timezone.utc)
            attempt = 0
            success = False
            last_error = None

            while attempt <= step.retries and not success:
                try:
                    if attempt > 0:
                        logger.warning("Retrying step [%s] attempt %d/%d", step.name, attempt, step.retries)

                    output = step.handler(current_input)
                    duration = (datetime.now(timezone.utc) - step_start).total_seconds() * 1000

                    self._log_step(step.name, "completed", current_input, output, duration_ms=duration)

                    results[step.name] = output
                    current_input = {**current_input, **output}
                    success = True

                except Exception as e:
                    attempt += 1
                    last_error = str(e)
                    logger.error("Step [%s] failed (attempt %d): %s", step.name, attempt, last_error)

                    if attempt > step.retries:
                        duration = (datetime.now(timezone.utc) - step_start).total_seconds() * 1000
                        self._log_step(step.name, "failed", current_input, None,
                                       error=f"{last_error}\n{traceback.format_exc()}", duration_ms=duration)

                        return {
                            "workflow_id": self.workflow_id,
                            "status": "failed",
                            "failed_step": step.name,
                            "error": last_error,
                            "completed_steps": list(results.keys()),
                            "results": results,
                            "execution_log": self.execution_log,
                        }

        logger.info("=== Workflow %s completed successfully ===", self.workflow_id)

        return {
            "workflow_id": self.workflow_id,
            "status": "completed",
            "results": results,
            "final_output": current_input,
            "execution_log": self.execution_log,
        }


def _summarize(data: Any, max_len: int = 500) -> Optional[str]:
    if data is None:
        return None
    s = str(data)
    return s[:max_len] + "..." if len(s) > max_len else s
