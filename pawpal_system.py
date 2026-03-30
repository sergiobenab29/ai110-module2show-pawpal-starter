from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import List, Optional


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


_PRIORITY_ORDER = {Priority.high: 0, Priority.medium: 1, Priority.low: 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority = Priority.medium
    completed: bool = False
    recurring: Optional[str] = None  # "daily", "weekly", or None
    notes: Optional[str] = None

    def mark_completed(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def is_due_today(self, date: datetime) -> bool:
        """Return True if this task should appear in today's schedule."""
        if self.recurring in (None, "daily"):
            return True
        if self.recurring == "weekly":
            return True
        return False


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int = 480
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


@dataclass
class ScheduleEntry:
    task: Task
    start: time
    end: time
    reason: str


@dataclass
class ScheduleResult:
    entries: List[ScheduleEntry] = field(default_factory=list)
    omitted_tasks: List[Task] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class Scheduler:
    @staticmethod
    def build_daily_schedule(
        owner: Owner,
        pet: Pet,
        day_start: time,
        day_end: time,
    ) -> ScheduleResult:
        """Build a priority-sorted schedule fitting all pending tasks into the given time window."""
        result = ScheduleResult()

        # Collect pending tasks from ALL owner pets, sorted by priority
        all_tasks: List[Task] = []
        for p in owner.pets:
            all_tasks.extend(p.get_pending_tasks())
        all_tasks.sort(key=lambda t: _PRIORITY_ORDER[t.priority])

        # Calculate available time window in minutes
        start_dt = datetime.combine(datetime.today(), day_start)
        end_dt = datetime.combine(datetime.today(), day_end)
        remaining = int((end_dt - start_dt).total_seconds() / 60)
        current_dt = start_dt

        for task in all_tasks:
            if task.duration_minutes <= remaining:
                task_end = current_dt + timedelta(minutes=task.duration_minutes)
                result.entries.append(
                    ScheduleEntry(
                        task=task,
                        start=current_dt.time(),
                        end=task_end.time(),
                        reason=f"Priority: {task.priority.value}",
                    )
                )
                current_dt = task_end
                remaining -= task.duration_minutes
            else:
                result.omitted_tasks.append(task)

        if result.omitted_tasks:
            result.warnings.append(
                f"{len(result.omitted_tasks)} task(s) skipped — not enough time in the day."
            )

        return result

    @staticmethod
    def detect_conflicts(pet: Pet) -> List[str]:
        """Check a pet's task list for time overloads or duplicate entries."""
        conflicts = []
        pending = pet.get_pending_tasks()

        total = sum(t.duration_minutes for t in pending)
        if total > 480:
            conflicts.append(
                f"{pet.name}'s tasks total {total} min, which exceeds a typical 8-hour day."
            )

        titles = [t.title for t in pending]
        seen: set = set()
        for title in titles:
            if titles.count(title) > 1 and title not in seen:
                conflicts.append(f"Duplicate task found: '{title}'")
                seen.add(title)

        return conflicts

    @staticmethod
    def explain_plan(schedule: ScheduleResult) -> str:
        """Return a human-readable summary of the schedule and any skipped tasks."""
        if not schedule.entries:
            return "No tasks were scheduled."

        lines = ["Plan for today:\n"]
        for entry in schedule.entries:
            lines.append(
                f"  {entry.start.strftime('%I:%M %p')} - {entry.end.strftime('%I:%M %p')}: "
                f"{entry.task.title} ({entry.task.priority.value} priority)"
            )

        if schedule.omitted_tasks:
            lines.append("\nSkipped (not enough time):")
            for task in schedule.omitted_tasks:
                lines.append(f"  - {task.title} ({task.duration_minutes} min)")

        if schedule.warnings:
            lines.append("\nWarnings:")
            for w in schedule.warnings:
                lines.append(f"  ! {w}")

        return "\n".join(lines)
