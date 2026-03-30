from datetime import date, time
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

# Create owner
owner = Owner(name="Alex", available_minutes_per_day=480)

# Create pets
dog = Pet(name="Buddy", species="Dog")
cat = Pet(name="Luna", species="Cat")

# Add tasks OUT OF ORDER to test sorting
dog.add_task(Task(title="Playtime", duration_minutes=20, priority=Priority.medium))
dog.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.high, recurring="daily"))
dog.add_task(Task(title="Feed breakfast", duration_minutes=10, priority=Priority.high, recurring="daily"))

cat.add_task(Task(title="Grooming", duration_minutes=15, priority=Priority.low, notes="Use soft brush"))
cat.add_task(Task(title="Feed breakfast", duration_minutes=5, priority=Priority.high, recurring="daily"))
cat.add_task(Task(title="Clean litter box", duration_minutes=10, priority=Priority.medium, recurring="daily"))

# Mark one task done to test filtering
dog.tasks[0].mark_completed()  # Playtime marked done

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler()

# Build and display schedule
schedule = scheduler.build_daily_schedule(
    owner=owner,
    pet=dog,
    day_start=time(8, 0),
    day_end=time(10, 0),
)

print("=" * 40)
print(f"  PawPal+ — Daily Schedule for {owner.name}")
print("=" * 40)
print(scheduler.explain_plan(schedule))

# Sort entries by start time and show
print("\n--- Sorted by Start Time ---")
for entry in scheduler.sort_by_time(schedule):
    print(f"  {entry.start.strftime('%I:%M %p')} - {entry.task.title}")

# Filter: only pending tasks
print("\n--- All Pending Tasks ---")
for t in scheduler.filter_tasks(owner, completed=False):
    print(f"  [ ] {t.title} ({t.duration_minutes} min, {t.priority.value})")

# Filter: only completed tasks
print("\n--- Completed Tasks ---")
for t in scheduler.filter_tasks(owner, completed=True):
    print(f"  [x] {t.title}")

# Filter: only Buddy's tasks
print("\n--- Buddy's Tasks ---")
for t in scheduler.filter_tasks(owner, pet_name="Buddy"):
    print(f"  {t.title} — done: {t.completed}")

# Recurring task demo — mark Morning walk done, then refresh
print("\n--- Recurring Task Demo ---")
dog.tasks[1].mark_completed()  # Mark Morning walk done
dog.refresh_recurring_tasks(today=date.today())
print(f"  Buddy's tasks after completing 'Morning walk':")
for t in dog.tasks:
    due = t.due_date.strftime("%Y-%m-%d") if t.due_date else "—"
    status = "done" if t.completed else f"due {due}"
    print(f"    {t.title} [{status}]")

# Conflict check (overloads / duplicates)
print("\n--- Conflict Check ---")
for pet in owner.pets:
    issues = scheduler.detect_conflicts(pet)
    if issues:
        for issue in issues:
            print(f"  [!] {issue}")
    else:
        print(f"  {pet.name}: no conflicts")

# Schedule conflict demo — manually create two overlapping entries
print("\n--- Schedule Overlap Demo ---")
from pawpal_system import ScheduleEntry, ScheduleResult
overlap_schedule = ScheduleResult(entries=[
    ScheduleEntry(task=Task(title="Vet appointment", duration_minutes=60, priority=Priority.high),
                  start=time(9, 0), end=time(10, 0), reason="fixed"),
    ScheduleEntry(task=Task(title="Morning walk", duration_minutes=30, priority=Priority.high),
                  start=time(9, 30), end=time(10, 0), reason="fixed"),
])
conflicts = scheduler.detect_schedule_conflicts(overlap_schedule)
if conflicts:
    for c in conflicts:
        print(f"  [!] {c}")
else:
    print("  No overlaps detected.")
