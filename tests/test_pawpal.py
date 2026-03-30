from pawpal_system import Task, Pet, Priority


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
