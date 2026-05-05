# Requirements

## 1. Purpose

This document summarizes the main requirements for the project **Task Allocation Assistant for Team and Project Management**.

The system is a rule-based decision-support assistant for task allocation. It does not use Machine Learning, Artificial Intelligence, or Generative AI.

---

## 2. Functional Requirements

## 2.1 Project Management

- The system shall allow the manager to create projects.
- The system shall allow the manager to view all projects.
- The system shall allow the manager to view a project by ID.
- The system shall allow the manager to delete projects.

Category: DB / CRUD-oriented functionality.

---

## 2.2 Team Member Management

- The system shall allow the manager to add team members to a project.
- The system shall store team member profiles.
- The system shall store availability, workload, reliability, dynamic status, and mood state.
- The system shall allow the manager to view team members by project.
- The system shall allow the manager to delete team members.

Category: DB / CRUD-oriented functionality with connection to complex functionality.

---

## 2.3 Skill Management

- The system shall allow the manager to create skills.
- The system shall allow the manager to assign skills to team members.
- The system shall allow the manager to define required skills for tasks.
- The system shall classify skills using a predefined taxonomy.

Category: DB / CRUD-oriented functionality and complex functionality.

---

## 2.4 Task Management

- The system shall allow the manager to create tasks.
- The system shall store task priority, deadline, status, and estimated effort.
- The system shall allow the manager to update task status.
- The system shall allow the manager to view tasks by project.

Category: DB / CRUD-oriented functionality.

---

## 2.5 Automatic Task Allocation

- The system shall calculate candidate scores for a task.
- The system shall use required skills, taxonomy match, availability, workload, reliability, dynamic status, mood, priority, and deadline urgency.
- The system shall select the best candidate if the score is above the threshold.
- The system shall create an assignment.
- The system shall update task status and member workload.
- The system shall move the task to manual review if no suitable candidate exists.
- The system shall provide a score breakdown and explanation.

Category: Complex functionality.

---

## 2.6 Delayed Task Reassignment

- The system shall reassign delayed tasks.
- The system shall find the current active assignment.
- The system shall exclude the current assignee from replacement candidates.
- The system shall exclude unavailable members.
- The system shall score replacement candidates.
- The system shall create a new assignment if a replacement is found.
- The system shall move the task to manual review if no replacement is suitable.

Category: Complex functionality.

---

## 2.7 Template-Based Project Decomposition

- The system shall provide predefined project templates.
- The manager shall select project components and complexity levels.
- The system shall generate tasks from selected components.
- The system shall attach required skills to generated tasks.
- The system shall map complexity to priority and estimated effort.
- The system shall prevent duplicate task generation by default.
- The system shall optionally generate and allocate multiple tasks.

Category: Complex functionality.

---

## 2.8 Workload Analysis and Conflict Detection

- The system shall analyze workload distribution.
- The system shall identify overloaded and underused members.
- The system shall detect when multiple tasks compete for the same best candidate.
- The system shall suggest conflict resolution based on priority and urgency.

Category: Complex functionality.

---

## 2.9 Notifications and Reminders

- The system shall create notifications for task assignment.
- The system shall create notifications for task reassignment.
- The system shall create notifications for manual review.
- The system shall create reminders for approaching deadlines.
- The system shall mark overdue tasks as delayed.
- The system shall avoid duplicate deadline reminders.

Category: Third-party / supporting service functionality.

---

## 3. Non-Functional Requirements

## 3.1 Usability

- The system should be understandable for managers and team leaders.
- Allocation results should include explanations.
- Swagger documentation should make API testing easy.

## 3.2 Maintainability

- The project should separate routers, models, schemas, and services.
- Complex logic should be implemented in service files.
- Tests should be organized by functionality.

## 3.3 Testability

- The system should include automated tests.
- Complex workflows should be covered by unit tests.
- The current expected test result is `49 passed`.

## 3.4 Explainability

- The system should explain allocation decisions.
- Candidate ranking should include score breakdowns.
- The allocation logic should remain transparent and rule-based.

## 3.5 Reliability

- The system should avoid duplicate deadline reminders.
- The system should prevent more than one active assignment for the same task.
- The system should move uncertain cases to manual review instead of forcing weak automatic decisions.

---

## 4. Requirement Categories Summary

| Category | Examples |
|---|---|
| DB / CRUD-oriented | projects, team members, skills, tasks, assignments, notifications |
| Third-party / supporting services | FastAPI, SQLAlchemy, Pydantic, Swagger/OpenAPI, APScheduler, Pytest |
| Complex functionality | scoring, taxonomy, allocation, reassignment, workload analysis, conflict detection, template-based decomposition |

---

## 5. Conclusion

The requirements show that the project is balanced across the three required categories.

The main complex value of the system is the rule-based task allocation workflow, supported by detailed team member profiles, taxonomy, heuristic scoring, reassignment logic, workload analysis, and template-based project decomposition.
