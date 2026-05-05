# Final Report Outline

## 1. Introduction

Briefly introduce the project: **Task Allocation Assistant for Team and Project Management**.

Explain that the system is a rule-based decision-support assistant for task allocation, not an AI/ML system.

---

## 2. Problem Statement

Describe the problem:

- manual task assignment is time-consuming;
- managers may not know current workload clearly;
- tasks can be assigned without considering skills, availability, or deadlines;
- delayed tasks may not be reassigned efficiently.

---

## 3. Project Goal

The goal is to support managers in:

- creating projects;
- managing team members;
- assigning tasks;
- using structured profiles;
- allocating tasks through heuristic scoring;
- monitoring workload;
- reassigning delayed tasks.

---

## 4. Software Development Process

Chosen model:

```text
Incremental Development Model
```

Reason:

The system was developed step by step, starting from CRUD functionality and then adding supporting services and complex allocation logic.

---

## 5. Requirements Analysis

Include:

- functional requirements;
- non-functional requirements;
- user roles;
- user stories;
- backlog summary.

Reference documents:

- `docs/requirements.md`
- `docs/user_stories.md`
- `docs/backlog.md`

---

## 6. Functionality Categorization

Describe the three required categories.

## 6.1 DB / CRUD-Oriented Functionalities

Examples:

- projects;
- team members;
- skills;
- tasks;
- assignments;
- notifications.

## 6.2 Third-Party / Supporting Services

Examples:

- FastAPI;
- SQLAlchemy;
- Pydantic;
- Swagger/OpenAPI;
- APScheduler;
- Pytest.

## 6.3 Complex Functionalities

Examples:

- deep team member profiles;
- skill taxonomy;
- role ontology;
- profile scoring;
- automatic task allocation;
- delayed task reassignment;
- workload analysis;
- conflict detection;
- template-based project decomposition.

---

## 7. Increment 1: CRUD and Data Management

Describe implementation of:

- database models;
- project management;
- team member management;
- skills;
- tasks;
- assignments;
- notifications.

---

## 8. Increment 2: Supporting Services

Describe implementation of:

- Swagger documentation;
- notification service;
- deadline reminder service;
- APScheduler integration;
- automated tests.

---

## 9. Increment 3: Complex Allocation Logic

Describe implementation of:

- scoring formula;
- taxonomy;
- allocation engine;
- reassignment engine;
- workload analysis;
- conflict resolver.

---

## 10. Increment 4: Template-Based Project Decomposition

Describe implementation of:

- predefined templates;
- component selection;
- complexity mapping;
- task generation;
- required skill generation;
- generate-and-allocate workflow.

---

## 11. System Design

Include UML diagrams:

1. Use Case Diagram
2. Class Diagram
3. Activity Diagram: Automatic Task Allocation
4. Activity Diagram: Template-Based Project Decomposition
5. Sequence Diagram: Delayed Task Reassignment

Reference:

- `docs/uml_diagrams.md`

---

## 12. Implementation

Briefly describe:

- project structure;
- routers;
- services;
- models;
- tests;
- documentation.

Reference:

- `docs/project_structure.md`

---

## 13. Testing

Describe:

- testing approach;
- Pytest usage;
- tested components;
- current result.

Current result:

```text
49 passed
```

Reference:

- `docs/testing_plan.md`

---

## 14. Demonstration Scenario

Describe the main demo workflow:

1. Create project.
2. Add team members.
3. Add skills.
4. Create task.
5. Preview allocation.
6. Auto-allocate task.
7. Generate project tasks from template.
8. Run generate-and-allocate.
9. Show workload/conflict analysis.
10. Show notifications.

Reference:

- `docs/demo_scenario.md`

---

## 15. Evaluation

Evaluate whether the project satisfies the course requirements:

- balanced between CRUD, third-party/supporting services, and complex logic;
- complex features are implemented algorithmically;
- tests validate main workflows;
- UML diagrams describe complex behavior.

---

## 16. Conclusion

Summarize that the project successfully implements a rule-based task allocation assistant with structured profiles, heuristic scoring, workload analysis, reassignment, and template-based task generation.

Mention that the system does not use ML or AI, but still provides intelligent decision-support through transparent rule-based logic.
