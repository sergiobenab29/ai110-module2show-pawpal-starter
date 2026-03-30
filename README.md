# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit app that helps a pet owner plan daily care tasks for their pets. You enter your pets, add tasks with priorities, and the app builds a smart schedule that fits your day.

## 📸 Demo

<a href="/course_images/ai110/pawpal.png" target="_blank"><img src='/course_images/ai110/pawpal.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Features

- **Add multiple pets** — track dogs, cats, or any animal separately
- **Task management** — assign tasks to specific pets with duration, priority, and recurrence
- **Smart sorting** — tasks are scheduled high-priority first; ties broken by duration so more tasks fit
- **Recurring tasks** — mark a daily or weekly task done and the next occurrence is auto-created
- **Filtering** — view only pending or completed tasks, or filter by pet
- **Conflict warnings** — overlapping tasks or overloaded days show a warning instead of crashing
- **Interactive schedule** — generates a time-blocked daily plan displayed as a clean table

## Testing PawPal+

Run the full test suite with:

```bash
python3 -m pytest tests/ -v
```

The tests cover 12 behaviors across two categories:

- **Happy paths** — task completion, adding tasks, priority ordering, daily recurrence, and filtering by status
- **Edge cases** — empty pet schedule, tasks too long to fit, overlapping time conflicts, non-recurring tasks, and owner with no pets

Confidence level: ★★★★☆ — the core scheduling logic and edge cases are well covered. The main area not fully tested is the Streamlit UI layer.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```
