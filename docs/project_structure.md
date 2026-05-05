# Project Structure

## 1. Purpose

This document describes the current structure of the project **Task Allocation Assistant for Team and Project Management**.

The project is implemented as a FastAPI backend application with SQLAlchemy models, service-layer business logic, API routers, automated tests, and Software Engineering documentation.

The system is designed as a rule-based decision-support assistant for project and task allocation. It does not use Machine Learning, Artificial Intelligence, or Generative AI.

---

## 2. Current Project Tree

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
│   ├── test_project_template_router_logic.py
│   ├── test_reminder_service.py
│   └── test_notification_service.py
│
├── docs/
│   ├── allocation_algorithm.md
│   ├── template_based_project_decomposition.md
│   ├── testing_plan.md
│   ├── user_stories.md
│   ├── backlog.md
│   ├── uml_diagrams.md
│   ├── demo_scenario.md
│   └── project_structure.md
│
├── requirements.txt
├── README.md
└── task_allocation.db
```

---

## 3. Important Note About Local Database

The file:

```text
task_allocation.db
```

is a local SQLite database file.

It is used during local development and should not be pushed to GitHub.

The database file may contain local testing data created through Swagger or manual API testing.

---

# 4. Main Application Files

## 4.1 app/main.py

This is the main entry point of the FastAPI application.

Responsibilities:

- create the FastAPI app instance;
- include API routers;
- create database tables;
- define application startup behavior;
- start the scheduler service;
- define application shutdown behavior;
- provide health check endpoint.

Main purpose:

```text
Application initialization and API router registration.
```

---

## 4.2 app/database.py

This file contains database configuration.

Responsibilities:

- define database URL;
- create SQLAlchemy engine;
- create session factory;
- define base model class;
- provide database session dependency.

Main purpose:

```text
Database connection and SQLAlchemy session management.
```

---

## 4.3 app/models.py

This file contains SQLAlchemy database models.

Main models:

- User
- Project
- TeamMember
- Skill
- TeamMemberSkill
- Task
- TaskRequiredSkill
- Assignment
- Notification

Main purpose:

```text
Database schema and entity relationships.
```

Important note:

The `TeamMember` model contains deep profile attributes such as:

- role;
- availability;
- workload;
- reliability;
- dynamic status;
- mood state.

These attributes are used by the complex allocation logic.

---

## 4.4 app/schemas.py

This file contains Pydantic schemas.

Responsibilities:

- define request models;
- define response models;
- validate API input;
- format API output.

Main purpose:

```text
Input/output validation for FastAPI endpoints.
```

---

## 4.5 app/auth.py

This file is reserved for authentication-related functionality.

Main purpose:

```text
Authentication and user-related support.
```

---

# 5. Routers

Routers define the API endpoints of the application.

## 5.1 app/routers/projects.py

Responsibilities:

- create projects;
- retrieve all projects;
- retrieve project by ID;
- delete projects.

Category:

```text
DB / CRUD-oriented functionality.
```

---

## 5.2 app/routers/team_members.py

Responsibilities:

- create team members;
- retrieve team members;
- retrieve team member by ID;
- retrieve team members by project;
- delete team members;
- assign skills to team members;
- retrieve skills of a team member.

Category:

```text
DB / CRUD-oriented functionality.
```

Connection to complex logic:

Team member profile attributes are later used by the allocation algorithm.

---

## 5.3 app/routers/skills.py

Responsibilities:

- create skills;
- retrieve skills;
- retrieve skill by ID;
- delete skills.

Category:

```text
DB / CRUD-oriented functionality.
```

Connection to complex logic:

Skills are classified through taxonomy and used in task-member compatibility scoring.

---

## 5.4 app/routers/tasks.py

Responsibilities:

- create tasks;
- retrieve tasks;
- retrieve task by ID;
- retrieve tasks by project;
- delete tasks;
- update task status;
- add required skills to tasks;
- retrieve required skills of a task.

Category:

```text
DB / CRUD-oriented functionality.
```

Connection to complex logic:

Task priority, deadline, estimated effort, status, and required skills are used by allocation and reassignment workflows.

---

## 5.5 app/routers/assignments.py

Responsibilities:

- preview task allocation;
- automatically allocate task;
- retrieve assignments;
- retrieve assignments by task;
- retrieve assignments by team member;
- reassign delayed tasks.

Category:

```text
Complex functionality.
```

Main complex workflows:

- automatic single task allocation;
- delayed task reassignment;
- one active assignment rule.

---

## 5.6 app/routers/analytics.py

Responsibilities:

- workload analysis;
- redistribution suggestions;
- conflict detection;
- conflict suggestions;
- taxonomy endpoint;
- manual deadline check endpoint.

Category:

```text
Complex functionality and supporting service functionality.
```

Main purpose:

```text
Analytics and decision-support endpoints.
```

---

## 5.7 app/routers/notifications.py

Responsibilities:

- retrieve all notifications;
- retrieve notifications by user;
- mark notification as read.

Category:

```text
Supporting service functionality.
```

---

## 5.8 app/routers/project_templates.py

Responsibilities:

- retrieve available project templates;
- generate task list preview;
- generate decomposition summary;
- generate template tasks in a project;
- generate and allocate multiple tasks.

Category:

```text
Complex functionality.
```

Main workflow:

```text
Template-based project decomposition and multi-task allocation.
```

---

# 6. Services

Services contain the main business logic of the system.

## 6.1 app/services/profile_scoring.py

This file contains the multi-criteria scoring logic.

Responsibilities:

- calculate skill match score;
- calculate taxonomy match score;
- calculate availability score;
- calculate workload score;
- calculate reliability score;
- calculate dynamic status score;
- calculate mood score;
- calculate priority score;
- calculate deadline urgency score;
- calculate final weighted score;
- generate score breakdown;
- generate explanation.

Category:

```text
Complex functionality.
```

Why complex:

The service evaluates candidates using multiple criteria and a weighted heuristic formula.

---

## 6.2 app/services/taxonomy.py

This file contains the skill taxonomy and role ontology.

Responsibilities:

- define skill categories;
- define role categories;
- classify skills;
- calculate role-skill compatibility;
- calculate task-category match;
- explain taxonomy match;
- return taxonomy summary.

Category:

```text
Complex functionality.
```

Why complex:

The service allows the system to reason about compatibility between roles, skills, and task requirements.

---

## 6.3 app/services/allocation_engine.py

This file contains the automatic task allocation logic.

Responsibilities:

- retrieve task requirements;
- retrieve project team members;
- calculate scores for all candidates;
- sort candidates by score;
- select the best candidate;
- create assignment;
- update task status;
- update workload;
- create notification;
- close previous active assignments for the same task.

Category:

```text
Complex functionality.
```

Why complex:

The engine performs a multi-step allocation workflow using scoring, threshold checking, workload update, and notification creation.

---

## 6.4 app/services/reassignment_engine.py

This file contains delayed task reassignment logic.

Responsibilities:

- find current active assignment;
- exclude current assignee;
- exclude unavailable members;
- score replacement candidates;
- mark old assignment as reassigned;
- create new active assignment;
- update workloads;
- move task to manual review if no replacement exists;
- create notification.

Category:

```text
Complex functionality.
```

Why complex:

The workflow involves assignment history, candidate filtering, scoring, reassignment, workload update, and fallback logic.

---

## 6.5 app/services/workload_balancer.py

This file contains workload analysis and redistribution logic.

Responsibilities:

- analyze workload distribution;
- identify overloaded members;
- identify underused members;
- suggest redistribution opportunities.

Category:

```text
Complex functionality.
```

---

## 6.6 app/services/conflict_resolver.py

This file contains conflict detection and conflict suggestion logic.

Responsibilities:

- detect when multiple tasks compete for the same best candidate;
- analyze open tasks;
- compare task priorities;
- suggest conflict resolution.

Category:

```text
Complex functionality.
```

---

## 6.7 app/services/project_template_service.py

This file contains template-based project decomposition logic.

Responsibilities:

- define predefined project templates;
- define template components;
- map components to task titles;
- map components to required skills;
- map complexity to priority;
- map complexity to estimated effort;
- generate tasks from selected components;
- generate decomposition summary.

Category:

```text
Complex functionality.
```

Why complex:

This service performs structured project decomposition without AI or ML. It uses predefined templates, rules, mappings, and validation.

---

## 6.8 app/services/notification_service.py

This file contains notification logic.

Responsibilities:

- create notification;
- retrieve all notifications;
- retrieve notifications by user;
- mark notification as read;
- create assignment notification;
- create reassignment notification;
- create manual review notification.

Category:

```text
Supporting service functionality.
```

---

## 6.9 app/services/reminder_service.py

This file contains deadline reminder and overdue task logic.

Responsibilities:

- find tasks with approaching deadlines;
- create deadline reminder notifications;
- prevent duplicate reminders;
- detect overdue tasks;
- mark overdue tasks as delayed;
- ignore completed tasks;
- run full deadline check workflow.

Category:

```text
Supporting service functionality with workflow logic.
```

---

## 6.10 app/services/scheduler_service.py

This file contains scheduler startup and shutdown logic.

Responsibilities:

- start APScheduler;
- run deadline checks on schedule;
- shut down scheduler.

Category:

```text
Third-party library integration.
```

Third-party library:

```text
APScheduler
```

---

# 7. Templates

The `app/templates/` directory contains HTML templates for a possible simple frontend.

Current templates:

- base.html
- dashboard.html
- projects.html
- tasks.html
- team_members.html

Current status:

```text
Planned / partially prepared for frontend demonstration.
```

The main project value is still in the backend logic and documentation.

---

# 8. Tests

The `tests/` directory contains automated tests written with Pytest.

Current test files:

- test_profile_scoring.py
- test_allocation_engine.py
- test_reassignment_engine.py
- test_project_template_service.py
- test_project_template_router_logic.py
- test_reminder_service.py
- test_notification_service.py

Current test result:

```text
49 passed
```

## 8.1 Tested Complex Logic

The tests cover:

- profile scoring;
- automatic allocation;
- delayed reassignment;
- template-based project decomposition;
- duplicate task prevention;
- reminder workflow;
- notification workflow.

This demonstrates that the main complex logic is validated through automated tests.

---

# 9. Documentation

The `docs/` directory contains Software Engineering documentation and project artifacts.

Current documentation files:

- allocation_algorithm.md
- template_based_project_decomposition.md
- testing_plan.md
- user_stories.md
- backlog.md
- uml_diagrams.md
- demo_scenario.md
- project_structure.md

## 9.1 allocation_algorithm.md

Explains the scoring formula and automatic task allocation workflow.

## 9.2 template_based_project_decomposition.md

Explains structured project generation and multi-task allocation.

## 9.3 testing_plan.md

Explains the testing strategy and tested components.

## 9.4 user_stories.md

Describes user stories from the perspective of the manager, team member, and system.

## 9.5 backlog.md

Organizes project features into epics, priorities, statuses, and categories.

## 9.6 uml_diagrams.md

Describes planned UML diagrams for the final report.

## 9.7 demo_scenario.md

Provides a step-by-step demonstration scenario for Swagger or project presentation.

---

# 10. Category Mapping

## 10.1 DB / CRUD-Oriented Parts

Main files:

- app/models.py
- app/database.py
- app/schemas.py
- app/routers/projects.py
- app/routers/team_members.py
- app/routers/skills.py
- app/routers/tasks.py

Main functionalities:

- project CRUD;
- team member CRUD;
- skill CRUD;
- task CRUD;
- required skill relations;
- assignments;
- notifications.

---

## 10.2 Third-Party / Supporting Service Parts

Main files:

- app/services/scheduler_service.py
- app/services/reminder_service.py
- app/services/notification_service.py
- tests/

Third-party tools and libraries:

- FastAPI;
- SQLAlchemy;
- Pydantic;
- Uvicorn;
- Swagger/OpenAPI;
- APScheduler;
- Pytest.

---

## 10.3 Complex Functionality Parts

Main files:

- app/services/profile_scoring.py
- app/services/taxonomy.py
- app/services/allocation_engine.py
- app/services/reassignment_engine.py
- app/services/workload_balancer.py
- app/services/conflict_resolver.py
- app/services/project_template_service.py
- app/routers/assignments.py
- app/routers/analytics.py
- app/routers/project_templates.py

Main complex workflows:

- deep team member profiles;
- taxonomy and ontology;
- multi-criteria scoring;
- automatic task allocation;
- delayed task reassignment;
- workload analysis;
- conflict detection;
- template-based project decomposition;
- multi-task allocation;
- manual review fallback.

---

# 11. How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run server:

```bash
uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Run tests:

```bash
PYTHONPATH=. pytest
```

Expected result:

```text
49 passed
```

---

# 12. Conclusion

The project structure separates the application into clear layers:

- routers for API endpoints;
- services for business logic;
- models for database entities;
- schemas for validation;
- tests for verification;
- docs for Software Engineering artifacts.

This structure supports maintainability and helps demonstrate that the project is balanced between CRUD functionality, third-party library usage, and complex rule-based application logic.
