# Task Allocation Assistant for Team and Project Management

A Software Engineering project developed as a rule-based intelligent project management assistant.

The system helps managers and team leaders create projects, manage team members, define tasks, attach required skills, automatically allocate tasks, monitor workload, detect conflicts, manually resolve assignment conflicts, reassign delayed tasks, manage notifications, and control project data through a web interface.

This project is not a simple task tracker. It is a decision-support system for task allocation and team coordination.

---

## Important Note

This project does **not** use Machine Learning, Artificial Intelligence, or Generative AI.

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

The goal of this project is to support managers in assigning and monitoring work more effectively by using structured team-member profiles and rule-based decision logic.

The system allows a manager to:

- create and manage projects;
- add and delete team members;
- create, search, and manage skills;
- remove global skills from the system when they are no longer needed;
- attach and remove skills from specialists;
- search employees across all projects;
- view project-specific team members;
- create and delete tasks;
- create tasks with deadlines, priorities, estimated effort, and required skills;
- automatically find the most suitable team member for a task;
- analyze workload distribution;
- detect assignment conflicts;
- resolve assignment conflicts directly from the Analytics page using manual assignment;
- reassign delayed tasks;
- receive and inspect notifications;
- generate multiple tasks from predefined project templates;
- create login accounts for existing employee profiles.

The system also allows team members to:

- log in to their own account;
- view their assigned tasks;
- update task status;
- update their own dynamic work status and mood state.

---

## Main User Roles

### Manager

The manager is responsible for project and team coordination.

Main manager capabilities:

- manage projects;
- manage team members;
- create and link login accounts for employees;
- manage skills and team-member skill profiles;
- remove global skills and remove skills from individual specialists;
- search employees globally and inspect project-specific team members;
- create tasks and structured project tasks;
- preview allocation results;
- run automatic task allocation;
- monitor task progress;
- inspect full employee profiles;
- inspect average allocation score in employee profiles;
- delete projects, members, and tasks;
- view all system notifications.

### Team Member

The team member has a limited personal workspace.

Main team-member capabilities:

- view assigned tasks;
- start and complete assigned tasks;
- update personal dynamic status;
- update personal mood state;
- receive personal notifications.

---

## Security and Access Control

The system includes basic role-based access control.

Important security decisions:

- Public registration creates only `team_member` accounts.
- Users cannot register themselves as `manager`.
- Manager accounts are created administratively.
- Manager pages are protected by role checks.
- Swagger/OpenAPI documentation is protected and accessible only to managers.
- Managers can create and link login accounts for existing team-member profiles.
- Passwords are stored as hashes, not as plain text.

This prevents unauthorized users from selecting the manager role through the registration page.

---

## Software Engineering Requirement Categories

The project is designed to be balanced across three required categories:

1. Data / Repository / DB-oriented functionalities
2. Third-party services and libraries
3. Complex functionalities implemented mostly by the developer

---

## 1. Data / Repository / DB-Oriented Functionalities

These functionalities are mainly based on storing, retrieving, updating, and deleting data from the database.

Implemented DB-oriented functionalities include:

- user management;
- project creation, listing, and deletion;
- team member creation, listing, profile display, and deletion;
- skill creation, listing, and deletion;
- team-member skill assignment and removal;
- task creation, listing, status update, and deletion;
- task required skills;
- assignment records;
- manual assignment records for conflict resolution;
- notifications;
- task statuses;
- project-based task and member retrieval;
- employee login account linking.

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

The project uses several third-party libraries and tools to support backend development, API documentation, database interaction, scheduling, templating, authentication, and testing.

Used technologies and libraries:

- FastAPI — backend web framework;
- Uvicorn — ASGI server;
- SQLAlchemy — ORM and database interaction;
- SQLite — local file-based database;
- Pydantic — request and response validation;
- Jinja2 — server-side HTML templates;
- Swagger / OpenAPI — automatic API documentation;
- APScheduler — scheduled deadline checking;
- passlib / bcrypt — password hashing;
- Pytest — automated testing.

Third-party-supported functionalities include:

- REST API documentation through Swagger;
- scheduled deadline checks using APScheduler;
- database interaction using SQLAlchemy;
- request validation using Pydantic;
- HTML rendering using Jinja2;
- password hashing;
- automated testing using Pytest.

---

## 3. Complex Functionalities

The main value of the project is in the complex application logic implemented inside the system.

These features are not simple CRUD operations. They use structured profiles, taxonomy, scoring formulas, constraints, and rule-based workflows.

---

### 3.1 Deep Team Member Profiles

Each team member has a structured profile that includes:

- role;
- availability;
- workload;
- reliability;
- dynamic status;
- mood state;
- hard skills;
- soft skills;
- assigned task history;
- linked login account information.

These attributes are used by the allocation algorithm when selecting the most suitable person for a task.

Managers can open a full employee profile page to inspect:

- profile summary;
- average allocation score;
- basic information;
- linked user account;
- deep profile indicators;
- skills;
- assignment history.

---

### 3.2 Team Member Mood and Status Self-Update

The system does not infer mood automatically.

Instead, mood and dynamic status are structured indicators explicitly updated by the team member.

A team member can update:

- dynamic status: `available`, `busy`, `focused`, `blocked`;
- mood state: `positive`, `neutral`, `stressed`.

The allocation algorithm then uses these updated values during future task assignment.

This keeps the system rule-based and explainable.

---

### 3.3 Skill Taxonomy and Role Ontology

The system uses a predefined taxonomy of skills and role categories.

Example skill categories:

- backend development;
- frontend development;
- database development;
- data analysis;
- testing;
- documentation;
- soft skills.

Example roles:

- Backend Developer;
- Frontend Developer;
- Database Developer;
- Data Analyst;
- QA Tester;
- Technical Writer;
- Project Manager.

This allows the system to reason about compatibility between task requirements and team member profiles.

---

### 3.4 Multi-Criteria Profile Scoring

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

The score is stored in the assignment record as `score_at_assignment`. Employee profiles use this stored value to display an Average Allocation Score, showing how suitable the employee was for tasks assigned by the allocation logic.

---

### 3.5 Automatic Single Task Allocation

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

If no candidate is suitable, the task is moved to manual review.

---

### 3.6 Manual Review Fallback

If the system cannot find a suitable candidate, it does not assign the task randomly.

Instead, it moves the task to manual review.

This happens when:

- no team member has the required skills;
- all candidates have low scores;
- workload or availability constraints reduce suitability;
- role and taxonomy compatibility are weak.

This is important because the system is designed as a decision-support assistant, not as an unsafe automatic decision-maker.

---

### 3.7 Delayed Task Reassignment

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

### 3.8 Workload Analysis

The system analyzes workload distribution inside a project.

It helps detect:

- overloaded team members;
- underused team members;
- balanced team members;
- workload imbalance;
- possible redistribution opportunities.

This supports better project coordination and fairer task distribution.

---

### 3.9 Conflict Detection and Manual Conflict Resolution

The system can detect assignment conflicts.

For example, if several open tasks have the same best candidate, the system identifies this conflict and shows the competing tasks, candidate score, risk level, and reason.

This prevents unrealistic allocation where one person receives too many important tasks at the same time.

The Analytics page also allows the manager to resolve a detected conflict directly from the web interface. For each competing task, the manager can choose an alternative team member from the same project and manually assign the task.

Conflict resolution workflow:

1. The system detects that several open tasks compete for the same best candidate.
2. The Analytics page shows the conflict, risk level, and competing tasks.
3. The manager reviews task priority, deadline, effort, and candidate score.
4. The manager keeps the most important task for the best candidate.
5. The manager assigns remaining tasks to alternative team members using the dropdown in the conflict card.
6. The system creates or updates the assignment, updates task status, adjusts workload, and creates a notification.

This keeps the system explainable: the algorithm detects the risk, but the manager can make the final decision when human judgement is needed.

---

### 3.10 Template-Based Project Decomposition and Multi-Task Allocation

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
5. Can run automatic allocation for generated tasks.
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

### 3.11 Controlled Delete Workflows

The manager can delete projects, team members, and tasks from the UI.

Delete workflows are controlled to preserve system consistency.

#### Delete Project

When a project is deleted, the system removes:

- project;
- project tasks;
- task assignments;
- task required skills;
- team members in the project;
- team member skills.

#### Delete Team Member

When a team member is deleted:

- the team member is removed;
- their skills are removed;
- their assignments are removed;
- assigned/in-progress/delayed tasks are released back to `open`;
- released tasks can be allocated again to another suitable team member.

#### Delete Task

When a task is deleted, the system removes:

- task;
- task assignments;
- task required skills.

This adds complete CRUD behavior while still preserving allocation logic.

---

### 3.12 Team Member Login Account Creation

Managers can create and link login accounts for existing team-member profiles.

Workflow:

1. Manager opens a team member full profile.
2. If the profile is not linked to a user account, the manager enters email and temporary password.
3. The system creates a `team_member` user account.
4. The password is hashed.
5. The new user account is linked to the existing team-member profile.

This avoids manual database editing and makes account management easier.

---

## Main Web Pages

The system includes a server-side rendered web interface.

Main UI pages:

- `/login` — login page;
- `/register` — public registration for team members;
- `/` — manager dashboard;
- `/projects-ui` — project management;
- `/team-members-ui` — team member management, global employee search, and project-specific team members;
- `/team-members-ui/{team_member_id}` — full employee profile;
- `/skills-ui` — skill creation, global skill removal, skill assignment, and specialist skill removal;
- `/tasks-ui` — task creation, progress monitoring, allocation actions, template generation;
- `/analytics-ui` — workload analysis, conflict detection, manual conflict resolution, and redistribution suggestions;
- `/notifications-ui` — notifications page;
- `/my-tasks` — team member personal task page.

---

## Recent UI Improvements

The latest version includes several UI and workflow improvements:

- employee profiles now display Average Allocation Score based on stored assignment scores;
- the Team Members page supports global employee search across all projects;
- the Team Members page also preserves project-specific member listing with View Full Profile and Delete Member actions;
- the Skills page supports deleting a global skill from the system;
- the Skills page still supports removing a skill only from a selected specialist;
- the Analytics page displays workload and conflict results as readable cards instead of raw JSON;
- conflict detection includes manager actions, allowing a competing task to be manually assigned to another team member directly from the Analytics page;
- analytics values such as workload, availability, and reliability are formatted consistently.

These changes improve the demonstration flow and make the system easier to explain during the project defence.

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
POST /assignments/manual-assign
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

### Protected UI Actions

```http
POST /projects-ui/{project_id}/delete
POST /team-members-ui/{team_member_id}/delete
POST /team-members-ui/{team_member_id}/create-user-account
POST /tasks-ui/{task_id}/delete
POST /skills-ui/team-members/{team_member_id}/skills/{skill_id}/remove
DELETE /skills/{skill_id}
POST /my-profile/status
POST /my-tasks/{assignment_id}/status
POST /notifications-ui/{notification_id}/read
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
│   │   ├── project_templates.py
│   │   └── users.py
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
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── projects.html
│   │   ├── team_members.html
│   │   ├── team_member_profile.html
│   │   ├── skills.html
│   │   ├── tasks.html
│   │   ├── analytics.html
│   │   ├── notifications.html
│   │   └── my_tasks.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│
├── tests/
│   ├── test_allocation_engine.py
│   ├── test_conflict_resolver.py
│   ├── test_crud.py
│   ├── test_notification_service.py
│   ├── test_profile_scoring.py
│   ├── test_project_template_router_logic.py
│   ├── test_project_template_service.py
│   ├── test_reassignment_engine.py
│   ├── test_reminder_service.py
│   └── test_workload_balancer.py
│
├── docs/
│   ├── backlog.md
│   ├── requirements.md
│   ├── uml_diagrams.md
│   ├── testing_plan.md
│   ├── project_structure.md
│   ├── final_report_outline.md
│   └── demo_scenario.md
│
├── requirements.txt
├── README.md
└── task_allocation.db
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

### 5. Open the web interface

```text
http://127.0.0.1:8000
```

### 6. Open protected Swagger documentation

```text
http://127.0.0.1:8000/docs
```

Swagger is protected and requires manager login.

---

## How to Run Tests

```bash
PYTHONPATH=. pytest
```

The project includes automated tests for:

- CRUD operations;
- profile scoring;
- allocation engine;
- delayed task reassignment;
- workload balancing;
- conflict detection;
- notification service;
- reminder service;
- project template service;
- project template router logic.

---

## Demo Workflow

A possible demonstration scenario:

1. Log in as manager.
2. Create a project.
3. Add team members with different roles and profiles.
4. Create skills and attach them to team members.
5. Create a task with required skills.
6. Preview candidate scoring.
7. Run automatic allocation.
8. Open the assigned employee profile.
9. Log in as the team member.
10. Update mood/status.
11. Start and complete the assigned task.
12. Return as manager and view notifications.
13. Use Team Members page to search employees globally and inspect project-specific members.
14. Use Skills page to remove a global skill or remove a skill from a specialist.
15. Delete a team member and show that their task is released for reallocation.
16. Generate multiple tasks from a project template.
17. Show workload analytics and conflict detection.
18. Resolve a conflict directly from Analytics by manually assigning a competing task to another team member.

---

## Current Implementation Status

Implemented:

- FastAPI backend;
- SQLite database;
- SQLAlchemy models;
- CRUD endpoints;
- protected manager routes;
- public team-member registration;
- password hashing;
- team member profiles;
- full employee profile UI;
- manager-created login accounts for employees;
- skill taxonomy;
- role ontology;
- skill assignment and skill removal;
- global skill deletion from the UI;
- employee global search and project-specific team member view;
- profile scoring;
- Average Allocation Score display in employee profiles;
- automatic task allocation;
- manual review fallback;
- delayed task reassignment;
- workload analysis;
- conflict detection;
- conflict suggestions;
- manual conflict resolution from the Analytics page;
- deadline reminders;
- notification system;
- manager notification visibility;
- team member mood/status self-update;
- controlled delete workflows for projects, members, and tasks;
- template-based project decomposition;
- multi-task generation and allocation;
- automated tests.

Not included:

- Machine Learning;
- Generative AI;
- external email verification service;
- production deployment configuration.

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
8. Increment 2: Authentication, UI, and Supporting Services
9. Increment 3: Complex Allocation Logic
10. Increment 4: Monitoring, Notifications, and Reassignment
11. Increment 5: Template-Based Project Decomposition and Multi-Task Allocation
12. Increment 6: Final UI, Delete Workflows, and Account Linking
13. UML Diagrams
    - Use Case Diagram
    - Class Diagram
    - Activity Diagram for Single Task Allocation
    - Activity Diagram for Template-Based Project Decomposition
    - Sequence Diagram for Delayed Task Reassignment
    - Activity Diagram for Deadline Reminder and Overdue Detection
    - Activity Diagram for Team Member Account Linking
14. Testing
15. Evaluation
16. Conclusion

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
