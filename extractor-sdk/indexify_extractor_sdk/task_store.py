from . import coordinator_service_pb2

from typing import Dict, List

from pydantic import BaseModel
from .ingestion_api_models import ApiContent, ApiFeature


class CompletedTask(BaseModel):
    task_id: str
    task_outcome: str
    new_content: List[ApiContent]
    features: List[ApiFeature]


class TaskStore:
    def __init__(self) -> None:
        self._tasks: Dict[str, coordinator_service_pb2.Task] = {}
        self._running_tasks: Dict[str, coordinator_service_pb2.Task] = {}
        self._finished: Dict[str, CompletedTask] = {}

    def get_task(self, id) -> coordinator_service_pb2.Task:
        return self._tasks[id]

    def add_tasks(self, tasks: List[coordinator_service_pb2.Task]):
        for task in tasks:
            if (
                (task.id in self._tasks)
                or (task.id in self._running_tasks)
                or (task.id in self._finished)
            ):
                continue
            print(f"added task {task.id} to queue")
            self._tasks[task.id] = task

    def get_runnable_tasks(self) -> Dict[str, coordinator_service_pb2.Task]:
        runnable_tasks = set(self._tasks) - set(self._running_tasks)
        runnable_tasks = set(runnable_tasks) - set(self._finished)
        out = {}
        for task_id in runnable_tasks:
            out[task_id] = self._tasks[task_id]
            self._running_tasks[task_id] = self._tasks[task_id]
        return out

    def complete(self, outcome: CompletedTask):
        self._finished[outcome.task_id] = outcome
        if outcome.task_id in self._running_tasks:
            self._running_tasks.pop(outcome.task_id)

    def mark_reported(self, task_id: str):
        self._tasks.pop(task_id)
        self._finished.pop(task_id)

    def report_failed(self, task_id: str):
        if self._finished[task_id].task_outcome != "Failed":
            # An error occurred while reporting the task, mark it as failed
            # and try reporting again.
            self._finished[task_id].task_outcome = "Failed"
        else:
            # If a task is already marked as failed, remove it from the queue.
            # The only possible error at this point is task not present at
            # the coordinator.
            self._tasks.pop(task_id)

    def num_pending_tasks(self) -> int:
        return len(self._tasks) + len(self._running_tasks)

    def task_outcomes(self) -> List[CompletedTask]:
        return self._finished.copy().values()
