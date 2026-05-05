# Demo Scenario

## 1. Purpose

This document describes a practical demonstration scenario for the project **Task Allocation Assistant for Team and Project Management**.

The goal of the demo is to show that the system is not a simple task tracker. It supports project management, structured team-member profiles, rule-based task allocation, template-based project decomposition, delayed task reassignment, workload analysis, conflict detection, deadline checking, and notifications.

The demo can be performed through Swagger UI.

Swagger URL:

```text
http://127.0.0.1:8000/docs
```

---

## 2. Before Starting the Demo

Start the backend server:

```bash
uvicorn app.main:app --reload
```

Run tests before the demo:

```bash
PYTHONPATH=. pytest
```

Expected result:

```text
49 passed
```

---

## 3. Main Demo Goal

The main goal of the demo is to show three types of functionality required by the Software Engineering project:

1. **DB / CRUD-oriented functionality**
   - creating projects;
   - adding team members;
   - adding skills;
   - creating tasks;
   - assigning required skills.

2. **Third-party / supporting services**
   - Swagger/OpenAPI documentation;
   - APScheduler deadline check support;
   - notifications;
   - automated testing with Pytest.

3. **Complex functionality**
   - deep team-member profiles;
   - skill taxonomy and role ontology;
   - multi-criteria heuristic scoring;
   - automatic task allocation;
   - template-based project decomposition;
   - multi-task allocation;
   - delayed task reassignment;
   - workload analysis;
   - conflict detection;
   - manual review fallback.

---

# 4. Demo Part 1: Basic Project Setup

## Step 1: Health Check

Endpoint:

```http
GET /health
```

Expected result:

```json
{
  "status": "ok"
}
```

Purpose:

This confirms that the backend server is running.

---

## Step 2: Create a Project

Endpoint:

```http
POST /projects/
```

Example request:

```json
{
  "title": "Website Development Project",
  "description": "A demo project for testing task allocation and structured project decomposition.",
  "deadline": "2026-06-30T23:59:00"
}
```

Expected result:

- A new project is created.
- Save the returned project `id`.

Purpose:

This demonstrates basic DB / CRUD functionality.

---

# 5. Demo Part 2: Create Team Members with Deep Profiles

## Step 3: Add Backend Developer

Endpoint:

```http
POST /team-members/
```

Example request:

```json
{
  "name": "Ali",
  "role": "Backend Developer",
  "availability": 0.9,
  "workload": 0.2,
  "reliability": 0.9,
  "dynamic_status": "available",
  "mood_state": "focused",
  "project_id": 1
}
```

Expected result:

- Team member Ali is created.
- Save Ali's `id`.

---

## Step 4: Add Frontend Developer

Endpoint:

```http
POST /team-members/
```

Example request:

```json
{
  "name": "Maria",
  "role": "Frontend Developer",
  "availability": 0.8,
  "workload": 0.3,
  "reliability": 0.85,
  "dynamic_status": "available",
  "mood_state": "normal",
  "project_id": 1
}
```

Expected result:

- Team member Maria is created.
- Save Maria's `id`.

---

## Step 5: Add Data Analyst / Database-Oriented Member

Endpoint:

```http
POST /team-members/
```

Example request:

```json
{
  "name": "John",
  "role": "Data Analyst",
  "availability": 0.6,
  "workload": 0.6,
  "reliability": 0.75,
  "dynamic_status": "busy",
  "mood_state": "normal",
  "project_id": 1
}
```

Expected result:

- Team member John is created.
- Save John's `id`.

---

## What to Explain

At this point, explain that team members are not simple names in the database. Each member has a structured profile:

- role;
- availability;
- workload;
- reliability;
- dynamic status;
- mood state.

These values are later used by the allocation algorithm.

---

# 6. Demo Part 3: Create Skills and Assign Them to Members

## Step 6: Create Skills

Endpoint:

```http
POST /skills/
```

Create these skills one by one:

```json
{
  "skill_name": "Python",
  "type": "hard",
  "level": "advanced"
}
```

```json
{
  "skill_name": "FastAPI",
  "type": "hard",
  "level": "advanced"
}
```

```json
{
  "skill_name": "API Design",
  "type": "hard",
  "level": "intermediate"
}
```

```json
{
  "skill_name": "JavaScript",
  "type": "hard",
  "level": "advanced"
}
```

```json
{
  "skill_name": "HTML",
  "type": "hard",
  "level": "intermediate"
}
```

```json
{
  "skill_name": "CSS",
  "type": "hard",
  "level": "intermediate"
}
```

```json
{
  "skill_name": "SQL",
  "type": "hard",
  "level": "advanced"
}
```

```json
{
  "skill_name": "Communication",
  "type": "soft",
  "level": "intermediate"
}
```

```json
{
  "skill_name": "Problem Solving",
  "type": "soft",
  "level": "advanced"
}
```

Expected result:

- Skills are created.
- Save the returned skill IDs.

---

## Step 7: Assign Skills to Team Members

Endpoint:

```http
POST /team-members/skills/
```

Example requests:

Assign backend skills to Ali:

```json
{
  "team_member_id": 1,
  "skill_id": 1
}
```

```json
{
  "team_member_id": 1,
  "skill_id": 2
}
```

```json
{
  "team_member_id": 1,
  "skill_id": 3
}
```

Assign frontend skills to Maria:

```json
{
  "team_member_id": 2,
  "skill_id": 4
}
```

```json
{
  "team_member_id": 2,
  "skill_id": 5
}
```

```json
{
  "team_member_id": 2,
  "skill_id": 6
}
```

Assign SQL and soft skills to John:

```json
{
  "team_member_id": 3,
  "skill_id": 7
}
```

```json
{
  "team_member_id": 3,
  "skill_id": 8
}
```

```json
{
  "team_member_id": 3,
  "skill_id": 9
}
```

Expected result:

- Team members now have different skill profiles.

---

## What to Explain

Explain that skills are later classified through taxonomy, for example:

- Python, FastAPI, API Design → backend development;
- JavaScript, HTML, CSS → frontend development;
- SQL → data / database category;
- Communication, Problem Solving → soft skills.

---

# 7. Demo Part 4: Automatic Single Task Allocation

## Step 8: Create a Backend Task

Endpoint:

```http
POST /tasks/
```

Example request:

```json
{
  "title": "Develop backend API",
  "description": "Create REST API endpoints for the web application.",
  "priority": "high",
  "deadline": "2026-06-10T23:59:00",
  "status": "open",
  "estimated_effort": 0.3,
  "project_id": 1
}
```

Expected result:

- A new task is created.
- Save task `id`.

---

## Step 9: Add Required Skills to the Task

Endpoint:

```http
POST /tasks/required-skills/
```

Add Python, FastAPI, and API Design as required skills.

Example requests:

```json
{
  "task_id": 1,
  "skill_id": 1
}
```

```json
{
  "task_id": 1,
  "skill_id": 2
}
```

```json
{
  "task_id": 1,
  "skill_id": 3
}
```

Expected result:

- The task now has required skills.

---

## Step 10: Preview Allocation

Endpoint:

```http
GET /assignments/preview/{task_id}
```

Example:

```http
GET /assignments/preview/1
```

Expected result:

The response should include:

- best candidate;
- candidate scores;
- score breakdown;
- explanation;
- positive factors;
- risk factors;
- required skills;
- member skills;
- taxonomy explanation.

What to show:

- Ali should receive a high score because he has backend skills and good availability.
- Maria may have lower score because her skills are frontend-oriented.
- John may have lower score due to workload and different role.

---

## Step 11: Run Automatic Allocation

Endpoint:

```http
POST /assignments/auto-allocate/{task_id}
```

Example:

```http
POST /assignments/auto-allocate/1
```

Expected result:

- The task is assigned to the best candidate.
- Assignment record is created.
- Task status becomes `assigned`.
- Selected member workload increases.
- Notification is created.

What to explain:

This is a complex functionality because it uses weighted heuristic scoring and constraints, not a simple database query.

---

# 8. Demo Part 5: Template-Based Project Decomposition

## Step 12: View Available Templates

Endpoint:

```http
GET /project-templates/
```

Expected result:

- The system returns available templates.
- Example template: `website_development`.

---

## Step 13: Generate Template Summary

Endpoint:

```http
POST /project-templates/generate-summary
```

Example request:

```json
{
  "template_key": "website_development",
  "selected_components": [
    {
      "component_key": "backend_api",
      "complexity": "high"
    },
    {
      "component_key": "frontend_pages",
      "complexity": "medium"
    },
    {
      "component_key": "database_design",
      "complexity": "high"
    },
    {
      "component_key": "authentication",
      "complexity": "high"
    },
    {
      "component_key": "testing",
      "complexity": "medium"
    }
  ]
}
```

Expected result:

- The system shows which tasks will be generated.
- It shows required skills.
- It shows complexity mapping to priority and effort.

---

## Step 14: Generate and Allocate Multiple Tasks

Endpoint:

```http
POST /project-templates/projects/{project_id}/generate-and-allocate
```

Example:

```http
POST /project-templates/projects/1/generate-and-allocate
```

Example request:

```json
{
  "template_key": "website_development",
  "allow_duplicates": false,
  "selected_components": [
    {
      "component_key": "backend_api",
      "complexity": "high"
    },
    {
      "component_key": "frontend_pages",
      "complexity": "medium"
    },
    {
      "component_key": "database_design",
      "complexity": "high"
    },
    {
      "component_key": "authentication",
      "complexity": "high"
    },
    {
      "component_key": "testing",
      "complexity": "medium"
    }
  ]
}
```

Expected result:

The system should:

- create multiple tasks;
- create or reuse required skills;
- attach required skills to tasks;
- automatically allocate each task;
- return allocation summary;
- show scores and explanations;
- move tasks to manual review if no candidate is suitable.

What to explain:

This is one of the strongest complex features because it combines:

- structured project decomposition;
- component-to-task mapping;
- required skills generation;
- complexity-to-priority mapping;
- duplicate protection;
- multi-task allocation;
- manual review fallback.

---

## Step 15: Show Duplicate Protection

Run the same generate-and-allocate request again with:

```json
{
  "allow_duplicates": false
}
```

Expected result:

- Existing generated tasks should be skipped.
- Skipped tasks should be returned in the response.

What to explain:

This shows business logic and prevents accidental duplicate task creation.

---

# 9. Demo Part 6: Workload Analysis and Conflict Detection

## Step 16: Run Workload Analysis

Endpoint:

```http
GET /analytics/project/{project_id}/workload
```

Example:

```http
GET /analytics/project/1/workload
```

Expected result:

- The system returns workload information for team members.
- It helps identify overloaded or underused members.

---

## Step 17: Run Redistribution Suggestions

Endpoint:

```http
GET /analytics/project/{project_id}/redistribution-suggestions
```

Example:

```http
GET /analytics/project/1/redistribution-suggestions
```

Expected result:

- The system returns possible workload redistribution suggestions.

---

## Step 18: Run Conflict Detection

Endpoint:

```http
GET /analytics/project/{project_id}/conflicts
```

Example:

```http
GET /analytics/project/1/conflicts
```

Expected result:

- The system detects cases where several open tasks compete for the same best candidate.

---

## Step 19: Run Conflict Suggestions

Endpoint:

```http
GET /analytics/project/{project_id}/conflict-suggestions
```

Example:

```http
GET /analytics/project/1/conflict-suggestions
```

Expected result:

- The system suggests which task should keep the best candidate based on priority.
- Other tasks may be suggested for manual review or alternative assignment.

What to explain:

This shows team-level reasoning, not only single-task assignment.

---

# 10. Demo Part 7: Delayed Task Reassignment

## Step 20: Mark a Task as Delayed

Endpoint:

```http
PATCH /tasks/{task_id}/status
```

Example:

```http
PATCH /tasks/1/status
```

Example request:

```json
{
  "status": "delayed"
}
```

Expected result:

- The task status becomes `delayed`.

---

## Step 21: Reassign Delayed Task

Endpoint:

```http
POST /assignments/reassign-delayed/{task_id}
```

Example:

```http
POST /assignments/reassign-delayed/1
```

Expected result:

If a replacement is found:

- current assignee is excluded;
- unavailable members are excluded;
- remaining candidates are scored;
- old assignment becomes `reassigned`;
- new assignment is created;
- workloads are updated;
- task status becomes `assigned`;
- notification is created.

If no replacement is found:

- task moves to `manual_review`;
- notification is created.

What to explain:

This is a complex workflow because it uses assignment history, candidate filtering, scoring, workload updates, and fallback logic.

---

# 11. Demo Part 8: Deadline Reminder and Overdue Detection

## Step 22: Run Manual Deadline Check

Endpoint:

```http
POST /analytics/deadline-check
```

Expected result:

The response should include:

- number of deadline reminders created;
- number of overdue tasks updated.

What to show:

- Tasks with approaching deadlines create reminder notifications.
- Overdue tasks become delayed.
- Completed tasks are ignored.
- Duplicate reminders are prevented.

---

# 12. Demo Part 9: Notifications

## Step 23: View All Notifications

Endpoint:

```http
GET /notifications/
```

Expected result:

The system returns notifications created during the demo, such as:

- task assignment notification;
- reassignment notification;
- manual review notification;
- deadline reminder notification;
- overdue task notification.

---

## Step 24: Mark Notification as Read

Endpoint:

```http
PATCH /notifications/{notification_id}/read
```

Example:

```http
PATCH /notifications/1/read
```

Expected result:

- `is_read` changes from `0` to `1`.

---

# 13. What to Emphasize During Presentation

During the demo, emphasize these points:

## 13.1 The project is not AI/ML-based

The system does not use Machine Learning, Artificial Intelligence, or Generative AI.

The decision-support behavior is implemented through:

- predefined rules;
- skill taxonomy;
- role ontology;
- weighted heuristic scoring;
- workload constraints;
- deadline urgency;
- priority;
- manual review fallback.

## 13.2 The complex part is rule-based and explainable

The system gives candidate scores and explanations, so the manager can understand why a person was selected.

## 13.3 The project is balanced

The project includes:

- DB / CRUD features;
- third-party libraries and supporting services;
- complex internal application logic.

## 13.4 Template-based decomposition is a strong feature

The manager can create a structured project by selecting predefined components and complexity levels. The system then generates and allocates multiple tasks automatically.

## 13.5 Manual review prevents weak automatic decisions

If the system cannot find a suitable candidate, it does not force an assignment. Instead, it marks the task for manual review.

---

# 14. Short Presentation Script

A short explanation for the demo:

```text
This project is a Task Allocation Assistant for team and project management.

It is not just a task tracker. The system stores projects, team members, skills, tasks, assignments, and notifications, but the main value is the allocation logic.

Each team member has a detailed profile with role, skills, availability, workload, reliability, dynamic status, and mood. The system uses a predefined skill taxonomy and role ontology, then calculates a weighted heuristic score for each candidate.

When a manager creates a task, the system can preview candidates, explain the score, and automatically assign the task to the most suitable member. If no candidate is suitable, the task goes to manual review.

The system also supports structured project creation. The manager selects a project template, components, and complexity. The system generates tasks, assigns required skills, and can allocate multiple tasks automatically.

Finally, the system supports delayed task reassignment, workload analysis, conflict detection, deadline reminders, and notifications.
```

---

# 15. Conclusion

This demo scenario shows the complete workflow of the project from basic CRUD operations to complex rule-based decision-support functionality.

The most important parts to demonstrate are:

1. Automatic task allocation with scoring and explanation.
2. Template-based project decomposition and multi-task allocation.
3. Delayed task reassignment.
4. Workload analysis and conflict detection.
5. Deadline reminders and notifications.

These workflows demonstrate that the project satisfies the Software Engineering requirement for complex functionalities implemented mostly by the developer.
