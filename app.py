import streamlit as st
from datetime import time
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Only create the Owner once — reuse it on every rerun
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_minutes_per_day=480)

owner: Owner = st.session_state.owner

st.title("🐾 PawPal+")

# --- Owner Info ---
st.subheader("Owner Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value=owner.name or "")
with col2:
    avail = st.number_input("Available minutes today", min_value=10, max_value=1440, value=owner.available_minutes_per_day)

if st.button("Save owner info"):
    owner.name = owner_name
    owner.available_minutes_per_day = avail
    st.success(f"Saved! Hi {owner.name}.")

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, species=species)
    owner.add_pet(new_pet)
    st.success(f"{pet_name} the {species} added!")

if owner.pets:
    st.write("Your pets:", [p.name for p in owner.pets])

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=Priority(priority),
        )
        selected_pet.add_task(new_task)
        st.success(f"Task '{task_title}' added to {selected_pet_name}.")

    # Show current tasks per pet
    for pet in owner.pets:
        pending = pet.get_pending_tasks()
        if pending:
            st.markdown(f"**{pet.name}'s tasks:**")
            st.table([{"title": t.title, "duration": t.duration_minutes, "priority": t.priority.value} for t in pending])

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

col1, col2 = st.columns(2)
with col1:
    day_start = st.time_input("Day starts at", value=time(8, 0))
with col2:
    day_end = st.time_input("Day ends at", value=time(18, 0))

if st.button("Generate schedule"):
    if not owner.pets or not owner.get_all_tasks():
        st.warning("Add at least one pet and one task first.")
    else:
        scheduler = Scheduler()
        schedule = scheduler.build_daily_schedule(
            owner=owner,
            pet=owner.pets[0],
            day_start=day_start,
            day_end=day_end,
        )
        st.text(scheduler.explain_plan(schedule))

        # Conflict check
        for pet in owner.pets:
            issues = scheduler.detect_conflicts(pet)
            for issue in issues:
                st.warning(issue)
