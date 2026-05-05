# Task Allocation Assistant for Team and Project Management

A Software Engineering project developed as a rule-based intelligent project management assistant.

The system helps managers and team leaders create projects, manage team members, define tasks, assign required skills, automatically allocate tasks, analyze workload, detect conflicts, and reassign delayed tasks using transparent heuristic logic.

This project is not a simple task tracker. It is a decision-support system for task allocation and team coordination.

## Important Note

This project does not use Machine Learning, Artificial Intelligence, or Generative AI.

The “intelligent” behavior of the system is implemented through:

- predefined rules;
- skill taxonomy;
- role ontology;
- weighted heuristic scoring;
- workload constraints;
- availability checks;
- reliability evaluation;
- dynamic status and mood indicators;
- priority and deadline urgency;
- manual review fallback.

This makes the allocation logic explainable, testable, and suitable for a Software Engineering university project.

---

## Project Goal

The goal of this project is to support managers in assigning tasks more effectively by using structured team-member profiles and rule-based decision logic.

The system allows a manager to:

- create and manage projects;
- add team members;
- define hard and soft skills;
- create tasks with deadlines, priorities, and required skills;
- automatically find the most suitable team member for a task;
- analyze workload distribution;
- detect assignment conflicts;
- reassign delayed tasks;
- receive notifications and deadline reminders;
- generate multiple tasks from predefined project templates.

---

## Software Engineering Requirement Categories

The project is designed to be balanced across three required categories:

1. Data / Repository / DB-oriented functionalities
2. Third-party services and libraries
3. Complex functionalities implemented mostly by the developer

---

## 1. Data / Repository / DB-Oriented Functionalities

These functionalities are mainly based on storing, retrieving, updating, and deleting data from the database.

Implemented CRUD-oriented functionalities include:

- user management;
- project creation and management;
- team member management;
- skill management;
- team member skill assignment;
- task creation and management;
- task required skills;
- assignment records;
- notifications;
- task statuses;
- project-based task and member retrieval.

Main database entities:

- User
- Project
- TeamMember
- Skill
- TeamMemberSkill
- Task
- TaskRequiredSkill
- Assignment
- Notification

These functionalities form the data foundation of the system.

---

## 2. Third-Party Services and Libraries

The project uses several third-party libraries and tools to support backend development, API documentation, database interaction, scheduling, and testing.

Used technologies and libraries:

- FastAPI — backend web framework;
- Uvicorn — ASGI server;
- SQLAlchemy — ORM and database interaction;
- SQLite — local database;
- Pydantic — request and response validation;
- Swagger / OpenAPI — automatic API documentation;
- APScheduler — scheduled deadline checking;
- Pytest — automated testing.

Third-party-supported functionalities include:

- REST API documentation through Swagger;
- scheduled deadline checks using APScheduler;
- database interaction using SQLAlchemy;
- request validation using Pydantic;
- automated testing using Pytest.

---

## 3. Complex Functionalities

The main value of the project is in the complex application logic implemented inside the system.

These features are not simple CRUD operations. They use structured profiles, taxonomy, scoring formulas, constraints, and rule-based workflows.

### 3.1 Deep Team Member Profiles

Each team member has a structured profile that includes:

- role;
- availability;
- workload;
- reliability;
- dynamic status;
- mood state;
- hard skills;
- soft skills.

These attributes are used by the allocation algorithm when selecting the most suitable person for a task.

---

### 3.2 Skill Taxonomy and Role Ontology

The system uses a predefined taxonomy of skills and role categories.

Example skill categories:

- backend development;
- frontend development;
- data analysis;
- project management;
- soft skills.

Example role ontology:

- Backend Developer;
- Frontend Developer;
- Full Stack Developer;
- Data Analyst;
- Project Manager.

This allows the system to reason about compatibility between task requirements and team member profiles.

---

### 3.3 Multi-Criteria Profile Scoring

The system calculates a score for each candidate using several criteria.

Current scoring formula:

```text
final_score =
  skill_match * 0.30 +
  taxonomy_match * 0.10 +
  availability * 0.15 +
  workload_score * 0.15 +
  reliability * 0.10 +
  dynamic_status_score * 0.07 +
  mood_score * 0.03 +
  priority_score * 0.05 +
  deadline_urgency_score * 0.05
```

The scoring considers:

- required skills;
- taxonomy compatibility;
- availability;
- workload;
- reliability;
- dynamic status;
- mood;
- task priority;
- deadline urgency.

The system also returns an explanation and score breakdown, making the decision transparent.

---

### 3.4 Automatic Single Task Allocation

The system can automatically assign a task to the most suitable team member.

Workflow:

1. Retrieve the task.
2. Retrieve required skills.
3. Retrieve team members from the same project.
4. Calculate a score for every candidate.
5. Sort candidates by score.
6. Select the best candidate if the score is above the threshold.
7. Create an assignment.
8. Update the task status.
9. Increase the selected member workload.
10. Create a notification.

If no candidate is suitable, the task can be moved to manual review.

---

### 3.5 Delayed Task Reassignment

The system supports reassignment of delayed tasks.

Workflow:

1. Detect that the task is delayed.
2. Find the current active assignment.
3. Exclude the current assignee from replacement candidates.
4. Exclude unavailable members.
5. Recalculate candidate scores.
6. Select the best replacement.
7. Mark the old assignment as reassigned.
8. Create a new active assignment.
9. Update member workloads.
10. Notify the new assignee.

If no replacement is suitable, the task is moved to manual review.

---

### 3.6 Workload Analysis

The system analyzes workload distribution inside a project.

It helps detect:

- overloaded team members;
- underused team members;
- workload imbalance;
- possible redistribution opportunities.

This supports better project coordination and fairer task distribution.

---

### 3.7 Conflict Detection and Resolution Suggestions

The system can detect assignment conflicts.

For example, if several open tasks have the same best candidate, the system identifies this conflict and suggests which task should keep the candidate based on priority and urgency.

This prevents unrealistic allocation where one person receives too many important tasks at the same time.

---

### 3.8 Template-Based Project Decomposition and Multi-Task Allocation

The system supports two task creation modes:

1. Single Task Allocation
2. Structured Project / Multi-Task Allocation

In the structured project mode, the manager selects:

- project type;
- required components;
- complexity level for each component.

The system then:

1. Generates tasks from predefined templates.
2. Assigns required skills to each generated task.
3. Maps complexity to priority and estimated effort.
4. Prevents duplicate task creation by default.
5. Runs automatic allocation for every generated task.
6. Returns assigned members, scores, explanations, and manual review cases.

This feature is rule-based and does not use AI or free-text generation.

Example supported template:

```text
website_development
```

Example components:

- backend_api;
- frontend_pages;
- database_design;
- authentication;
- admin_panel;
- testing;
- documentation.

Example mapping:

```text
backend_api → Develop backend API
Required skills: Python, FastAPI, API Design
```

```text
frontend_pages → Build frontend pages
Required skills: JavaScript, HTML, CSS, UI Design
```

Complexity mapping:

```text
low    → priority = medium,   estimated_effort = 0.2
medium → priority = high,     estimated_effort = 0.3
high   → priority = critical, estimated_effort = 0.4
```

This is one of the strongest complex features of the project because it combines project decomposition, task generation, required skill mapping, workload-aware allocation, explainable scoring, and manual review fallback.

---

## Main API Endpoints

### Health Check

```http
GET /health
```

### Projects

```http
POST /projects/
GET /projects/
GET /projects/{project_id}
DELETE /projects/{project_id}
```

### Team Members

```http
POST /team-members/
GET /team-members/
GET /team-members/{team_member_id}
GET /team-members/project/{project_id}
DELETE /team-members/{team_member_id}
```

### Skills

```http
POST /skills/
GET /skills/
GET /skills/{skill_id}
DELETE /skills/{skill_id}
```

### Tasks

```http
POST /tasks/
GET /tasks/
GET /tasks/{task_id}
GET /tasks/project/{project_id}
DELETE /tasks/{task_id}
PATCH /tasks/{task_id}/status
```

### Team Member Skills

```http
POST /team-members/skills/
GET /team-members/{team_member_id}/skills
```

### Task Required Skills

```http
POST /tasks/required-skills/
GET /tasks/{task_id}/required-skills
```

### Assignments

```http
GET /assignments/preview/{task_id}
POST /assignments/auto-allocate/{task_id}
GET /assignments/
GET /assignments/task/{task_id}
GET /assignments/member/{team_member_id}
POST /assignments/reassign-delayed/{task_id}
```

### Analytics

```http
GET /analytics/project/{project_id}/workload
GET /analytics/project/{project_id}/redistribution-suggestions
GET /analytics/project/{project_id}/conflicts
GET /analytics/project/{project_id}/conflict-suggestions
GET /analytics/taxonomy
POST /analytics/deadline-check
```

### Project Templates

```http
GET /project-templates/
POST /project-templates/generate-tasks
POST /project-templates/generate-summary
POST /project-templates/projects/{project_id}/generate-template-tasks
POST /project-templates/projects/{project_id}/generate-and-allocate
```

### Notifications

```http
GET /notifications/
GET /notifications/user/{user_id}
PATCH /notifications/{notification_id}/read
```

---

## Example Template-Based Request

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
    }
  ]
}
```

---

## Project Structure

```text
task-allocation-assistant/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   │
│   ├── routers/
│   │   ├── projects.py
│   │   ├── team_members.py
│   │   ├── skills.py
│   │   ├── tasks.py
│   │   ├── assignments.py
│   │   ├── notifications.py
│   │   ├── analytics.py
│   │   └── project_templates.py
│   │
│   ├── services/
│   │   ├── allocation_engine.py
│   │   ├── reassignment_engine.py
│   │   ├── profile_scoring.py
│   │   ├── taxonomy.py
│   │   ├── workload_balancer.py
│   │   ├── conflict_resolver.py
│   │   ├── project_template_service.py
│   │   ├── notification_service.py
│   │   ├── reminder_service.py
│   │   └── scheduler_service.py
│   │
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── projects.html
│       ├── tasks.html
│       └── team_members.html
│
├── tests/
│   ├── test_profile_scoring.py
│   ├── test_allocation_engine.py
│   ├── test_reassignment_engine.py
│   ├── test_project_template_service.py
│   └── test_project_template_router_logic.py
│
├── docs/
│   ├── allocation_algorithm.md
│   └── template_based_project_decomposition.md
│
├── requirements.txt
└── README.md
```

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/astannnn/task-allocation-assistant.git
cd task-allocation-assistant
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

### 5. Open Swagger API Documentation

```text
http://127.0.0.1:8000/docs
```

---

## How to Run Tests

```bash
PYTHONPATH=. pytest
```

Current test status:

```text
36 passed
```

---

## Current Implementation Status

Implemented:

- FastAPI backend;
- SQLite database;
- SQLAlchemy models;
- CRUD endpoints;
- team member profiles;
- skill taxonomy;
- role ontology;
- profile scoring;
- automatic task allocation;
- delayed task reassignment;
- workload analysis;
- conflict detection;
- conflict suggestions;
- deadline reminders;
- notification system;
- template-based project decomposition;
- multi-task generation and allocation;
- automated tests.

Not yet fully completed:

- frontend interface;
- final Software Engineering report;
- additional tests for reminder and notification services;
- final UML diagrams;
- final project documentation.

---

## Planned Software Engineering Report Structure

The final report will follow an incremental development model.

Planned sections:

1. Introduction
2. Problem Statement
3. Project Goal and Motivation
4. Software Development Process: Incremental Model
5. Requirements Analysis
6. Functionalities Categorization
   - DB-oriented functionalities
   - Third-party services and libraries
   - Complex functionalities
7. Increment 1: CRUD and Data Management
8. Increment 2: Supporting Services and Notifications
9. Increment 3: Complex Allocation Logic
10. Increment 4: Template-Based Project Decomposition and Multi-Task Allocation
11. UML Diagrams
    - Use Case Diagram
    - Class Diagram
    - Activity Diagram for Single Task Allocation
    - Activity Diagram for Template-Based Project Decomposition
    - Sequence Diagram for Delayed Task Reassignment
    - Activity Diagram for Deadline Reminder and Overdue Detection
12. Testing
13. Evaluation
14. Conclusion

---

## Academic Relevance

This project is suitable for a Software Engineering course because it includes:

- structured requirements;
- database-oriented functionality;
- third-party libraries and services;
- complex internal application logic;
- incremental development;
- testable backend services;
- UML diagrams and documentation;
- explainable rule-based decision-making.

The most important complex part of the project is the task allocation workflow, which uses multi-criteria heuristic scoring, skill taxonomy, role ontology, workload balancing, deadline urgency, priority constraints, and reassignment logic.

---

## Author

Astan Tabyldy uulu

Bachelor of Data Analysis  
University of Messina  
Academic Year 2025/2026
