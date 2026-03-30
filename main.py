from datetime import time
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

# Create owner
owner = Owner(name="Alex", available_minutes_per_day=480)

# Create pets
dog = Pet(name="Buddy", species="Dog")
cat = Pet(name="Luna", species="Cat")

# Add tasks to dog
dog.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.high, recurring="daily"))
dog.add_task(Task(title="Feed breakfast", duration_minutes=10, priority=Priority.high, recurring="daily"))
dog.add_task(Task(title="Playtime", duration_minutes=20, priority=Priority.medium))

# Add tasks to cat
cat.add_task(Task(title="Feed breakfast", duration_minutes=5, priority=Priority.high, recurring="daily"))
cat.add_task(Task(title="Clean litter box", duration_minutes=10, priority=Priority.medium, recurring="daily"))
cat.add_task(Task(title="Grooming", duration_minutes=15, priority=Priority.low, notes="Use soft brush"))

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Build schedule
scheduler = Scheduler()
schedule = scheduler.build_daily_schedule(
    owner=owner,
    pet=dog,
    day_start=time(8, 0),
    day_end=time(10, 0),  # 2-hour window to test skipping
)

# Print results
print("=" * 40)
print(f"  PawPal+ — Daily Schedule for {owner.name}")
print("=" * 40)
print(scheduler.explain_plan(schedule))

# Check for conflicts
print("\n--- Conflict Check ---")
for pet in owner.pets:
    issues = scheduler.detect_conflicts(pet)
    if issues:
        for issue in issues:
            print(f"  [!] {issue}")
    else:
        print(f"  {pet.name}: no conflicts")
