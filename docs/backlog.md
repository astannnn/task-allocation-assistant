# Product Backlog

## 1. Purpose

This document presents the product backlog for the Software Engineering project **Task Allocation Assistant for Team and Project Management**.

The backlog organizes the project into epics and user stories. It also shows the priority and current implementation status of each feature.

The project follows an incremental development approach. Each increment adds a meaningful part of the system, starting from basic data management and continuing toward supporting services and complex allocation logic.

---

## 2. Development Approach

The project is developed using an incremental model.

The planned increments are:

1. **Increment 1: CRUD and Data Management**
   - projects;
   - team members;
   - skills;
   - tasks;
   - assignments;
   - notifications.

2. **Increment 2: Supporting Services**
   - API documentation;
   - notifications;
   - deadline reminders;
   - scheduled deadline checking;
   - automated testing.

3. **Increment 3: Complex Allocation Logic**
   - deep team member profiles;
   - skill taxonomy;
   - role ontology;
   - profile scoring;
   - automatic task allocation;
   - delayed task reassignment;
   - workload analysis;
   - conflict detection.

4. **Increment 4: Template-Based Project Decomposition**
   - structured project creation;
   - predefined project templates;
   - component-to-task mapping;
   - complexity mapping;
   - multi-task generation;
   - generate-and-allocate workflow.

5. **Increment 5: User Interface and Final Documentation**
   - simple frontend pages;
   - final UML diagrams;
   - final report;
   - demonstration scenario.

---

## 3. Priority Levels

The backlog uses the following priority levels:

- **High** — essential for the project and required for demonstrating the main idea.
- **Medium** — important, but not blocking the core functionality.
- **Low** — useful improvement or future extension.

---

## 4. Status Levels

The backlog uses the following status levels:

- **Completed** — implemented and tested.
- **Implemented** — implemented but may need more testing or documentation.
- **In Progress** — partially implemented.
- **Planned** — not implemented yet.
- **Future Improvement** — optional feature for future development.

---

# 5. Backlog Items

## Epic 1: Project and Team Data Management

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B1.1 | Create and manage projects | High | Implemented | DB / CRUD |
| B1.2 | Retrieve all projects | High | Implemented | DB / CRUD |
| B1.3 | Retrieve a single project by ID | High | Implemented | DB / CRUD |
| B1.4 | Delete a project | Medium | Implemented | DB / CRUD |
| B1.5 | Add team members to a project | High | Implemented | DB / CRUD |
| B1.6 | Retrieve team members by project | High | Implemented | DB / CRUD |
| B1.7 | Delete team members | Medium | Implemented | DB / CRUD |

### Notes

This epic provides the basic data structure of the system. It is mainly CRUD-oriented and forms the foundation for the complex allocation logic.

---

## Epic 2: Skills and Task Requirements

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B2.1 | Create skills | High | Implemented | DB / CRUD |
| B2.2 | Retrieve skills | High | Implemented | DB / CRUD |
| B2.3 | Delete skills | Medium | Implemented | DB / CRUD |
| B2.4 | Assign skills to team members | High | Implemented | DB / CRUD |
| B2.5 | Retrieve skills of a team member | High | Implemented | DB / CRUD |
| B2.6 | Add required skills to a task | High | Implemented | DB / CRUD |
| B2.7 | Retrieve required skills of a task | High | Implemented | DB / CRUD |

### Notes

This epic connects the data layer with the complex allocation logic because skills are later used by the scoring algorithm.

---

## Epic 3: Task Management

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B3.1 | Create tasks | High | Implemented | DB / CRUD |
| B3.2 | Retrieve all tasks | High | Implemented | DB / CRUD |
| B3.3 | Retrieve task by ID | High | Implemented | DB / CRUD |
| B3.4 | Retrieve tasks by project | High | Implemented | DB / CRUD |
| B3.5 | Delete tasks | Medium | Implemented | DB / CRUD |
| B3.6 | Update task status | High | Implemented | DB / CRUD |
| B3.7 | Store task priority | High | Implemented | DB / CRUD |
| B3.8 | Store task deadline | High | Implemented | DB / CRUD |
| B3.9 | Store estimated effort | High | Implemented | DB / CRUD |

### Notes

Task management is CRUD-oriented, but task attributes such as priority, deadline, status, and estimated effort are also used by the complex allocation and reassignment workflows.

---

## Epic 4: Deep Team Member Profiles

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B4.1 | Store team member role | High | Implemented | Complex |
| B4.2 | Store availability | High | Implemented | Complex |
| B4.3 | Store workload | High | Implemented | Complex |
| B4.4 | Store reliability | High | Implemented | Complex |
| B4.5 | Store dynamic status | High | Implemented | Complex |
| B4.6 | Store mood state | Medium | Implemented | Complex |
| B4.7 | Use profile attributes in scoring | High | Completed | Complex |

### Notes

This epic directly addresses the requirement for detailed team member profiles. The attributes are not only stored; they are used by the scoring algorithm to support decision-making.

---

## Epic 5: Skill Taxonomy and Role Ontology

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B5.1 | Define skill taxonomy | High | Completed | Complex |
| B5.2 | Define role ontology | High | Completed | Complex |
| B5.3 | Classify skills by category | High | Completed | Complex |
| B5.4 | Calculate role-skill compatibility | High | Completed | Complex |
| B5.5 | Calculate task-category match | High | Completed | Complex |
| B5.6 | Provide taxonomy explanation | Medium | Completed | Complex |
| B5.7 | Expose taxonomy endpoint | Medium | Implemented | Complex |

### Notes

This epic supports compatibility reasoning between task requirements and team member profiles. It keeps the project rule-based and explainable without using ML or AI.

---

## Epic 6: Profile Scoring

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B6.1 | Calculate skill match score | High | Completed | Complex |
| B6.2 | Calculate taxonomy match score | High | Completed | Complex |
| B6.3 | Calculate availability score | High | Completed | Complex |
| B6.4 | Calculate workload score | High | Completed | Complex |
| B6.5 | Calculate reliability score | High | Completed | Complex |
| B6.6 | Calculate dynamic status score | High | Completed | Complex |
| B6.7 | Calculate mood score | Medium | Completed | Complex |
| B6.8 | Calculate priority score | Medium | Completed | Complex |
| B6.9 | Calculate deadline urgency score | Medium | Completed | Complex |
| B6.10 | Generate final weighted score | High | Completed | Complex |
| B6.11 | Generate score explanation | High | Completed | Complex |
| B6.12 | Return score breakdown | High | Completed | Complex |

### Notes

This epic is one of the core algorithmic parts of the project. The scoring formula is transparent and based on predefined weights.

---

## Epic 7: Automatic Single Task Allocation

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B7.1 | Retrieve task requirements | High | Completed | Complex |
| B7.2 | Retrieve project team members | High | Completed | Complex |
| B7.3 | Score all candidates | High | Completed | Complex |
| B7.4 | Sort candidates by score | High | Completed | Complex |
| B7.5 | Select best candidate above threshold | High | Completed | Complex |
| B7.6 | Create assignment | High | Implemented | Complex |
| B7.7 | Update task status to assigned | High | Implemented | Complex |
| B7.8 | Increase selected member workload | High | Implemented | Complex |
| B7.9 | Create assignment notification | Medium | Implemented | Supporting Service |
| B7.10 | Close previous active assignments for the same task | High | Completed | Complex |
| B7.11 | Move task to manual review if no suitable candidate exists | High | Implemented | Complex |

### Notes

This epic represents the main decision-support workflow of the project.

---

## Epic 8: Delayed Task Reassignment

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B8.1 | Detect delayed task status | High | Completed | Complex |
| B8.2 | Find current active assignment | High | Completed | Complex |
| B8.3 | Exclude current assignee | High | Completed | Complex |
| B8.4 | Exclude unavailable members | High | Completed | Complex |
| B8.5 | Score replacement candidates | High | Completed | Complex |
| B8.6 | Mark old assignment as reassigned | High | Implemented | Complex |
| B8.7 | Create new active assignment | High | Implemented | Complex |
| B8.8 | Decrease previous member workload | High | Implemented | Complex |
| B8.9 | Increase new member workload | High | Implemented | Complex |
| B8.10 | Create reassignment notification | Medium | Implemented | Supporting Service |
| B8.11 | Move task to manual review if no replacement exists | High | Implemented | Complex |

### Notes

This epic is important for demonstrating algorithmic workflow logic through a sequence diagram in the final report.

---

## Epic 9: Workload Analysis and Conflict Resolution

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B9.1 | Analyze workload distribution | High | Implemented | Complex |
| B9.2 | Identify overloaded members | High | Implemented | Complex |
| B9.3 | Suggest redistribution opportunities | Medium | Implemented | Complex |
| B9.4 | Detect multiple tasks competing for same candidate | High | Implemented | Complex |
| B9.5 | Suggest conflict resolution based on priority | High | Implemented | Complex |

### Notes

This epic shows that the system does not only assign individual tasks, but also reasons about team-level workload and allocation conflicts.

---

## Epic 10: Template-Based Project Decomposition

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B10.1 | Define predefined project templates | High | Completed | Complex |
| B10.2 | Support website development template | High | Completed | Complex |
| B10.3 | Define template components | High | Completed | Complex |
| B10.4 | Map components to task titles | High | Completed | Complex |
| B10.5 | Map components to required skills | High | Completed | Complex |
| B10.6 | Map complexity to priority and effort | High | Completed | Complex |
| B10.7 | Generate tasks from selected components | High | Completed | Complex |
| B10.8 | Create required skills automatically if missing | High | Implemented | Complex |
| B10.9 | Prevent duplicate generated tasks by default | High | Completed | Complex |
| B10.10 | Allow duplicates when explicitly requested | Medium | Completed | Complex |
| B10.11 | Generate and allocate multiple tasks | High | Completed | Complex |
| B10.12 | Return allocation summary | High | Completed | Complex |
| B10.13 | Return manual review cases | High | Completed | Complex |

### Notes

This is one of the strongest complex features of the project. It supports structured project planning without AI or ML.

---

## Epic 11: Notifications

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B11.1 | Create notification | High | Completed | Supporting Service |
| B11.2 | Retrieve all notifications | Medium | Completed | Supporting Service |
| B11.3 | Retrieve notifications by user | Medium | Completed | Supporting Service |
| B11.4 | Mark notification as read | Medium | Completed | Supporting Service |
| B11.5 | Create assignment notification | High | Completed | Supporting Service |
| B11.6 | Create reassignment notification | High | Completed | Supporting Service |
| B11.7 | Create manual review notification | High | Completed | Supporting Service |
| B11.8 | Create deadline reminder notification | High | Completed | Supporting Service |
| B11.9 | Create overdue task notification | High | Completed | Supporting Service |

### Notes

Notifications support the main workflows of the project and help the manager track important system events.

---

## Epic 12: Deadline Reminder and Overdue Detection

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B12.1 | Find tasks with approaching deadlines | High | Completed | Supporting Service |
| B12.2 | Create deadline reminders | High | Completed | Supporting Service |
| B12.3 | Prevent duplicate deadline reminders | High | Completed | Supporting Service |
| B12.4 | Detect overdue tasks | High | Completed | Supporting Service |
| B12.5 | Mark overdue tasks as delayed | High | Completed | Supporting Service |
| B12.6 | Ignore completed tasks | High | Completed | Supporting Service |
| B12.7 | Run deadline check manually through endpoint | Medium | Implemented | Supporting Service |
| B12.8 | Run deadline check automatically with APScheduler | Medium | Implemented | Third-party Library |

### Notes

This epic uses APScheduler as a third-party library and combines it with internal reminder workflow logic.

---

## Epic 13: Testing

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B13.1 | Test profile scoring | High | Completed | Testing |
| B13.2 | Test allocation engine | High | Completed | Testing |
| B13.3 | Test reassignment engine | High | Completed | Testing |
| B13.4 | Test project template service | High | Completed | Testing |
| B13.5 | Test project template router logic | High | Completed | Testing |
| B13.6 | Test reminder service | High | Completed | Testing |
| B13.7 | Test notification service | High | Completed | Testing |
| B13.8 | Add endpoint integration tests | Medium | Planned | Testing |
| B13.9 | Add CRUD endpoint tests | Medium | Planned | Testing |

### Notes

Current automated test result:

```text
49 passed
```

---

## Epic 14: Documentation and Software Engineering Artifacts

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B14.1 | Write README | High | Completed | Documentation |
| B14.2 | Write testing plan | High | Completed | Documentation |
| B14.3 | Write user stories | High | Completed | Documentation |
| B14.4 | Write backlog | High | Completed | Documentation |
| B14.5 | Write allocation algorithm documentation | High | Implemented | Documentation |
| B14.6 | Write template decomposition documentation | High | Implemented | Documentation |
| B14.7 | Write UML diagram documentation | High | Planned | Documentation |
| B14.8 | Prepare final report | High | Planned | Documentation |
| B14.9 | Prepare demonstration scenario | Medium | Planned | Documentation |

### Notes

This epic supports the Software Engineering course requirement that the project report should describe development stages and include UML diagrams and related artifacts.

---

## Epic 15: User Interface

| ID | User Story / Feature | Priority | Status | Category |
|---|---|---:|---|---|
| B15.1 | Create base layout | Medium | Planned | Frontend |
| B15.2 | Create dashboard page | Medium | Planned | Frontend |
| B15.3 | Create projects page | Medium | Planned | Frontend |
| B15.4 | Create team members page | Medium | Planned | Frontend |
| B15.5 | Create tasks page | Medium | Planned | Frontend |
| B15.6 | Create structured project creation page | High | Planned | Frontend |
| B15.7 | Create analytics page | Medium | Planned | Frontend |
| B15.8 | Create notifications page | Medium | Planned | Frontend |

### Notes

The frontend is planned as a simple interface for demonstration purposes. The main project value remains in the backend logic and Software Engineering documentation.

---

# 6. Backlog Summary by Category

## 6.1 DB / CRUD-Oriented Functionalities

Main items:

- project management;
- team member management;
- skill management;
- task management;
- task required skills;
- assignments;
- notifications.

These are necessary for storing and managing the system data.

---

## 6.2 Third-Party / Supporting Services

Main items:

- FastAPI;
- SQLAlchemy;
- Pydantic;
- Swagger/OpenAPI;
- APScheduler;
- Pytest;
- notification workflow;
- deadline reminders.

These functionalities rely on external libraries or support the operation of the system.

---

## 6.3 Complex Functionalities

Main items:

- deep team member profiles;
- skill taxonomy;
- role ontology;
- multi-criteria profile scoring;
- automatic task allocation;
- delayed task reassignment;
- workload analysis;
- conflict detection;
- template-based project decomposition;
- multi-task generation and allocation;
- manual review fallback.

These functionalities are complex because their main value lies in internal logic, scoring, rule-based reasoning, and multi-step workflows.

---

# 7. Current Progress

Current approximate progress:

- DB / CRUD functionalities: mostly implemented;
- complex backend logic: mostly implemented;
- third-party and supporting services: implemented at backend level;
- automated tests: 49 passing tests;
- documentation: partially completed;
- frontend: planned;
- final report: planned.

---

# 8. Next Steps

Planned next steps:

1. Complete UML diagram documentation.
2. Add simple frontend pages for demonstration.
3. Add endpoint-level tests.
4. Prepare final report following the incremental model.
5. Prepare a final demo scenario.
6. Commit and push changes after the current documentation and tests are stable.

---

# 9. Conclusion

The backlog shows that the project is balanced across the required categories: DB-oriented functionalities, third-party/supporting services, and complex functionalities.

The strongest parts of the project are the rule-based allocation workflow, deep team member profiles, taxonomy-based compatibility, delayed task reassignment, workload analysis, conflict detection, and template-based project decomposition.

The project does not use ML or AI. The decision-support behavior is implemented through transparent heuristic logic and structured workflows.
