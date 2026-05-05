# User Stories

## 1. Purpose

This document describes the main user stories for the Software Engineering project **Task Allocation Assistant for Team and Project Management**.

The goal of these user stories is to describe the system from the point of view of its users and to connect the implemented functionalities with real project management needs.

The main users of the system are:

- Manager / Team Leader
- Team Member
- System / Scheduling Service

The project is designed as a rule-based decision-support system. It does not use Machine Learning, Artificial Intelligence, or Generative AI. The intelligent behavior is implemented through predefined rules, skill taxonomy, role ontology, heuristic scoring, workload analysis, and constraint-aware allocation workflows.

---

## 2. User Roles

## 2.1 Manager / Team Leader

The manager is the main user of the system.

The manager can:

- create and manage projects;
- add team members;
- define team member profiles;
- create tasks;
- define required skills;
- run automatic allocation;
- generate tasks from templates;
- monitor workload;
- check assignment conflicts;
- reassign delayed tasks;
- view notifications.

## 2.2 Team Member

The team member is the person who receives assigned tasks.

A team member has a structured profile that includes:

- role;
- hard skills;
- soft skills;
- availability;
- workload;
- reliability;
- dynamic status;
- mood state.

## 2.3 System / Scheduling Service

The system performs automatic operations such as:

- checking approaching deadlines;
- detecting overdue tasks;
- creating deadline reminder notifications;
- marking overdue tasks as delayed;
- supporting reassignment workflows.

---

## 3. Epic 1: Project and Team Management

## User Story 1.1: Create a Project

As a manager,  
I want to create a project with a title, description, and deadline,  
so that I can organize tasks and team members under one project.

### Acceptance Criteria

- The manager can create a new project.
- The project stores title, description, creation date, and deadline.
- The project can be retrieved from the system.
- The project can be deleted if needed.

### Category

Data / Repository / DB-oriented functionality.

---

## User Story 1.2: Add Team Members to a Project

As a manager,  
I want to add team members to a project,  
so that I can assign tasks only to people who belong to that project.

### Acceptance Criteria

- The manager can create a team member profile.
- The team member is connected to a project.
- The manager can view all team members of a project.
- The manager can delete a team member if needed.

### Category

Data / Repository / DB-oriented functionality.

---

## User Story 1.3: Maintain Deep Team Member Profiles

As a manager,  
I want to store detailed team member profiles,  
so that the system can use this information during automatic task allocation.

### Acceptance Criteria

Each team member profile includes:

- name;
- role;
- availability;
- workload;
- reliability;
- dynamic status;
- mood state.

The profile information is used by the scoring algorithm.

### Category

Complex functionality.

### Rationale

This is complex because the profile is not only stored in the database. It is also used as input for scoring, ranking, allocation, workload balancing, and reassignment decisions.

---

## 4. Epic 2: Skill Management and Taxonomy

## User Story 2.1: Create Skills

As a manager,  
I want to define skills,  
so that I can describe both team member abilities and task requirements.

### Acceptance Criteria

- The manager can create a skill.
- The manager can view all available skills.
- The manager can delete a skill.
- Skills can be assigned to team members.
- Skills can be required by tasks.

### Category

Data / Repository / DB-oriented functionality.

---

## User Story 2.2: Assign Skills to Team Members

As a manager,  
I want to assign hard and soft skills to team members,  
so that the system can evaluate their suitability for tasks.

### Acceptance Criteria

- A team member can have multiple skills.
- Skills can represent technical skills or soft skills.
- The system can retrieve all skills of a team member.

### Category

Data / Repository / DB-oriented functionality.

---

## User Story 2.3: Use Skill Taxonomy and Role Ontology

As a manager,  
I want the system to classify skills and roles using a predefined taxonomy,  
so that task-member compatibility can be evaluated more intelligently.

### Acceptance Criteria

- Skills are grouped into categories such as backend development, frontend development, data analysis, project management, and soft skills.
- Roles are mapped to related skill categories.
- The allocation logic uses taxonomy compatibility.
- The system can explain taxonomy-based matching.

### Category

Complex functionality.

### Rationale

This is complex because taxonomy and ontology are used to reason about compatibility between tasks and team members. The system does not only compare exact skill names, but also evaluates whether the member profile is generally compatible with the task category.

---

## 5. Epic 3: Task Management

## User Story 3.1: Create a Task

As a manager,  
I want to create tasks with priority, deadline, status, and estimated effort,  
so that project work can be planned and tracked.

### Acceptance Criteria

- The manager can create a task.
- The task belongs to a project.
- The task has a title, description, priority, deadline, status, and estimated effort.
- The manager can view tasks by project.
- The manager can update task status.

### Category

Data / Repository / DB-oriented functionality.

---

## User Story 3.2: Define Required Skills for a Task

As a manager,  
I want to assign required skills to a task,  
so that the system can evaluate which team member is suitable.

### Acceptance Criteria

- A task can have multiple required skills.
- Required skills are stored in the database.
- Required skills are used by the allocation algorithm.

### Category

Data / Repository / DB-oriented functionality with connection to complex functionality.

---

## 6. Epic 4: Automatic Single Task Allocation

## User Story 4.1: Preview Candidate Scores

As a manager,  
I want to preview candidate scores before assigning a task,  
so that I can understand which team member is most suitable and why.

### Acceptance Criteria

- The system retrieves all eligible team members from the project.
- The system calculates a score for each candidate.
- Candidates are sorted by score.
- The response includes score breakdown.
- The response includes an explanation of positive factors and risk factors.

### Category

Complex functionality.

### Rationale

This is complex because the system performs multi-criteria evaluation using required skills, taxonomy match, availability, workload, reliability, dynamic status, mood, priority, and deadline urgency.

---

## User Story 4.2: Automatically Allocate a Task

As a manager,  
I want the system to automatically assign a task to the best available team member,  
so that task allocation becomes faster and more consistent.

### Acceptance Criteria

- The system calculates candidate scores.
- The best candidate is selected if the score is above the threshold.
- An assignment is created.
- The task status becomes assigned.
- The selected member workload increases.
- A notification is created.
- If no suitable candidate exists, the task is moved to manual review.

### Category

Complex functionality.

### Rationale

This is one of the main algorithmically complex features. It combines candidate retrieval, skill matching, taxonomy matching, weighted scoring, threshold checking, workload update, assignment creation, and notification generation.

---

## User Story 4.3: Explain Allocation Decision

As a manager,  
I want to see why the system selected a specific team member,  
so that I can trust and verify the allocation decision.

### Acceptance Criteria

- The system returns a score breakdown.
- The system returns positive factors.
- The system returns risk factors.
- The explanation is understandable to the manager.

### Category

Complex functionality.

### Rationale

Explainability is important because the system is a decision-support tool. The manager should understand the logic behind the recommendation instead of receiving a hidden or unclear decision.

---

## 7. Epic 5: Template-Based Project Decomposition

## User Story 5.1: Choose Between Single Task and Structured Project

As a manager,  
I want to choose between creating a single task and creating a structured project,  
so that I can use the system for both small and larger project planning cases.

### Acceptance Criteria

- The manager can choose single task allocation.
- The manager can choose structured project generation.
- Structured project generation uses predefined templates.
- The system does not use free-text AI generation.

### Category

Complex functionality.

### Rationale

This supports two different workflows and keeps the project realistic, testable, and rule-based.

---

## User Story 5.2: Generate Tasks from a Project Template

As a manager,  
I want to select a project type, components, and complexity levels,  
so that the system can generate a structured list of tasks automatically.

### Acceptance Criteria

- The manager selects a template such as website development.
- The manager selects components such as backend API, frontend pages, database design, authentication, testing, and documentation.
- Each component is converted into a predefined task.
- Required skills are automatically attached to generated tasks.
- Complexity is mapped to priority and estimated effort.
- Duplicate tasks are skipped by default.

### Category

Complex functionality.

### Rationale

This is complex because the system performs rule-based project decomposition, component-to-task mapping, required skill generation, complexity mapping, duplicate protection, and database creation in one workflow.

---

## User Story 5.3: Generate and Allocate Multiple Tasks

As a manager,  
I want the system to generate several tasks from a template and allocate them automatically,  
so that I can quickly create and distribute work for a structured project.

### Acceptance Criteria

- The system generates tasks from selected components.
- The system creates required skills if they do not exist.
- The system links required skills to generated tasks.
- The system runs automatic allocation for each generated task.
- Each task is either assigned or moved to manual review.
- The response includes assignment results, scores, candidate scores, and explanations.

### Category

Complex functionality.

### Rationale

This is one of the strongest complex workflows of the project. It combines template-based decomposition, database task creation, required skill management, multi-task allocation, workload-aware scoring, and manual review fallback.

---

## 8. Epic 6: Delayed Task Reassignment

## User Story 6.1: Reassign a Delayed Task

As a manager,  
I want the system to reassign a delayed task to another suitable team member,  
so that project progress can continue when the current assignee cannot complete the task.

### Acceptance Criteria

- The task must have delayed status.
- The system finds the current active assignment.
- The current assignee is excluded from replacement candidates.
- Unavailable members are excluded.
- Alternative candidates are scored.
- The best replacement is selected.
- The old assignment becomes reassigned.
- A new active assignment is created.
- Workloads are updated.
- A notification is created.
- If no replacement exists, the task moves to manual review.

### Category

Complex functionality.

### Rationale

This is complex because it is a multi-step workflow involving assignment history, candidate exclusion, profile scoring, workload updates, reassignment status, and fallback behavior.

---

## 9. Epic 7: Workload Analysis and Conflict Detection

## User Story 7.1: Analyze Workload

As a manager,  
I want to see workload distribution across the team,  
so that I can identify overloaded and underused team members.

### Acceptance Criteria

- The system calculates workload information for team members.
- The system identifies workload imbalance.
- The system can suggest redistribution opportunities.

### Category

Complex functionality.

### Rationale

This is complex because the system interprets workload data and uses it to support management decisions, instead of only displaying stored records.

---

## User Story 7.2: Detect Assignment Conflicts

As a manager,  
I want the system to detect when several tasks compete for the same best candidate,  
so that I can avoid assigning too much work to one person.

### Acceptance Criteria

- The system evaluates open tasks.
- The system identifies cases where multiple tasks have the same best candidate.
- The system reports conflicts.
- The system suggests which task should keep the candidate based on priority and urgency.

### Category

Complex functionality.

### Rationale

This is complex because the system compares multiple allocation situations at the same time and identifies conflicts caused by limited suitable candidates.

---

## 10. Epic 8: Notifications and Deadline Reminders

## User Story 8.1: Receive Assignment Notifications

As a manager,  
I want the system to create a notification when a task is assigned,  
so that important allocation events are recorded and visible.

### Acceptance Criteria

- A notification is created after automatic assignment.
- The notification contains the task title.
- The notification contains the assigned team member name.
- The notification type is task_assigned.

### Category

Third-party / supporting service functionality.

---

## User Story 8.2: Receive Reassignment Notifications

As a manager,  
I want the system to create a notification when a delayed task is reassigned,  
so that I can track changes in responsibility.

### Acceptance Criteria

- A notification is created after reassignment.
- The notification contains the task title.
- The notification contains the previous assignee if available.
- The notification contains the new assignee.
- The notification type is task_reassigned.

### Category

Third-party / supporting service functionality.

---

## User Story 8.3: Receive Manual Review Notifications

As a manager,  
I want the system to notify me when a task cannot be automatically assigned,  
so that I can manually make a decision.

### Acceptance Criteria

- A notification is created when a task requires manual review.
- The notification contains the task title.
- The notification contains the reason for manual review.
- The notification type is manual_review.

### Category

Third-party / supporting service functionality.

---

## User Story 8.4: Receive Deadline Reminders

As a manager,  
I want the system to create reminders for tasks with approaching deadlines,  
so that I can react before tasks become overdue.

### Acceptance Criteria

- The system finds tasks with approaching deadlines.
- Completed tasks are ignored.
- Duplicate reminders are not created.
- A deadline_reminder notification is created.

### Category

Third-party / supporting service functionality.

### Rationale

This functionality is supported by APScheduler and reminder service logic. It helps the system monitor deadlines automatically.

---

## User Story 8.5: Detect Overdue Tasks

As a manager,  
I want the system to mark overdue tasks as delayed,  
so that delayed work can be identified and reassignment can be considered.

### Acceptance Criteria

- The system finds tasks with passed deadlines.
- Completed tasks are ignored.
- Already delayed tasks are ignored.
- Overdue tasks are marked as delayed.
- A task_delayed notification is created.

### Category

Third-party / supporting service functionality with workflow logic.

---

## 11. Epic 9: Manual Review

## User Story 9.1: Move Task to Manual Review

As a manager,  
I want the system to move a task to manual review when automatic allocation is not possible,  
so that I can make the final decision manually.

### Acceptance Criteria

- The system checks whether a suitable candidate exists.
- If no candidate reaches the required threshold, the task is not assigned automatically.
- The task status becomes manual_review.
- A notification explains the reason.

### Category

Complex functionality.

### Rationale

Manual review is part of the fallback logic. It prevents the system from making weak or unreliable automatic decisions.

---

## 12. Summary of User Stories by Category

## 12.1 Data / Repository / DB-Oriented User Stories

- Create a project.
- Add team members to a project.
- Create skills.
- Assign skills to team members.
- Create tasks.
- Define required skills for tasks.
- View and update task statuses.
- Store assignments and notifications.

## 12.2 Third-Party / Supporting Service User Stories

- Receive assignment notifications.
- Receive reassignment notifications.
- Receive manual review notifications.
- Receive deadline reminders.
- Detect overdue tasks through scheduled checks.
- Use Swagger/OpenAPI documentation.
- Run automated tests with Pytest.

## 12.3 Complex Functionality User Stories

- Maintain deep team member profiles.
- Use skill taxonomy and role ontology.
- Preview candidate scores.
- Automatically allocate a task.
- Explain allocation decision.
- Generate tasks from templates.
- Generate and allocate multiple tasks.
- Reassign delayed tasks.
- Analyze workload.
- Detect assignment conflicts.
- Move unsuitable tasks to manual review.

---

## 13. Conclusion

The user stories show that the system is not limited to simple task tracking. The project includes database management, supporting services, and complex decision-support workflows.

The most important complex user stories are related to automatic task allocation, template-based project decomposition, delayed task reassignment, workload analysis, and conflict detection. These stories directly support the Software Engineering requirement that complex functionalities should be based on internal application logic implemented by the developer.
