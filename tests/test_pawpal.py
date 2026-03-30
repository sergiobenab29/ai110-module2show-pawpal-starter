from datetime import date, time, timedelta
from pawpal_system import (
    Task, Pet, Owner, Scheduler, Priority,
    ScheduleEntry, ScheduleResult,
)


# --- Happy Paths ---

def test_mark_completed_changes_status():
    task = Task(title="Walk", duration_minutes=30, priority=Priority.high)
    assert task.completed is False
    task.mark_completed()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feed", duration_minutes=10, priority=Priority.medium))
    assert len(pet.tasks) == 1


def test_schedule_respects_priority_order():
    owner = Owner(name="Alex", available_minutes_per_day=480)
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(title="Low task", duration_minutes=10, priority=Priority.low))
    pet.add_task(Task(title="High task", duration_minutes=10, priority=Priority.high))
    owner.add_pet(pet)
    scheduler = Scheduler()
    schedule = scheduler.build_daily_schedule(owner, pet, time(8, 0), time(10, 0))
    assert schedule.entries[0].task.title == "High task"


def test_next_occurrence_daily_is_tomorrow():
    today = date.today()
    task = Task(title="Walk", duration_minutes=20, priority=Priority.high,
                recurring="daily", due_date=today)
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_filter_tasks_returns_only_pending():
    owner = Owner(name="Alex", available_minutes_per_day=480)
    pet = Pet(name="Luna", species="Cat")
    done = Task(title="Done task", duration_minutes=5, priority=Priority.low)
    done.mark_completed()
    pet.add_task(done)
    pet.add_task(Task(title="Pending task", duration_minutes=5, priority=Priority.medium))
    owner.add_pet(pet)
    pending = Scheduler.filter_tasks(owner, completed=False)
    assert all(not t.completed for t in pending)
    assert len(pending) == 1


# --- Edge Cases ---

def test_pet_with_no_tasks_returns_empty_schedule():
    owner = Owner(name="Alex", available_minutes_per_day=480)
    pet = Pet(name="Empty", species="Dog")
    owner.add_pet(pet)
    schedule = Scheduler.build_daily_schedule(owner, pet, time(8, 0), time(10, 0))
    assert schedule.entries == []
    assert schedule.omitted_tasks == []


def test_all_tasks_too_long_go_to_omitted():
    owner = Owner(name="Alex", available_minutes_per_day=480)
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(title="Very long task", duration_minutes=200, priority=Priority.high))
    owner.add_pet(pet)
    schedule = Scheduler.build_daily_schedule(owner, pet, time(8, 0), time(9, 0))  # 60 min window
    assert len(schedule.entries) == 0
    assert len(schedule.omitted_tasks) == 1


def test_detect_schedule_conflicts_catches_overlap():
    overlap_schedule = ScheduleResult(entries=[
        ScheduleEntry(task=Task(title="Task A", duration_minutes=60, priority=Priority.high),
                      start=time(9, 0), end=time(10, 0), reason="fixed"),
        ScheduleEntry(task=Task(title="Task B", duration_minutes=30, priority=Priority.high),
                      start=time(9, 30), end=time(10, 0), reason="fixed"),
    ])
    conflicts = Scheduler.detect_schedule_conflicts(overlap_schedule)
    assert len(conflicts) == 1
    assert "Task A" in conflicts[0]


def test_next_occurrence_on_non_recurring_returns_none():
    task = Task(title="One-time task", duration_minutes=10, priority=Priority.medium)
    assert task.next_occurrence() is None


def test_owner_with_no_pets_returns_empty_task_list():
    owner = Owner(name="Alex", available_minutes_per_day=480)
    assert owner.get_all_tasks() == []


def test_sort_by_time_returns_chronological_order():
    # Build a schedule with entries intentionally out of order
    t1 = ScheduleEntry(task=Task(title="Early", duration_minutes=10, priority=Priority.low),
                       start=time(8, 0), end=time(8, 10), reason="")
    t2 = ScheduleEntry(task=Task(title="Late", duration_minutes=10, priority=Priority.low),
                       start=time(10, 0), end=time(10, 10), reason="")
    t3 = ScheduleEntry(task=Task(title="Middle", duration_minutes=10, priority=Priority.low),
                       start=time(9, 0), end=time(9, 10), reason="")
    schedule = ScheduleResult(entries=[t2, t3, t1])  # added out of order
    sorted_entries = Scheduler.sort_by_time(schedule)
    titles = [e.task.title for e in sorted_entries]
    assert titles == ["Early", "Middle", "Late"]


def test_recurring_task_creates_next_occurrence_after_completion():
    today = date.today()
    pet = Pet(name="Buddy", species="Dog")
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.high,
                recurring="daily", due_date=today)
    pet.add_task(task)
    task.mark_completed()
    pet.refresh_recurring_tasks(today)
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].title == "Morning walk"
    assert pending[0].due_date == today + timedelta(days=1)
