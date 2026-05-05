# UML Diagrams

## 1. Purpose

This document describes the main UML diagrams planned for the project **Task Allocation Assistant for Team and Project Management**.

The diagrams are intended to support the Software Engineering report by showing:

- the main users of the system;
- the structure of the main entities;
- the most important workflows;
- the algorithmically complex parts of the project.

The project is not a simple task tracker. It is a rule-based decision-support system for task allocation. Therefore, the most important diagrams are the ones that explain automatic allocation, template-based project decomposition, and delayed task reassignment.

---

## 2. Planned Diagrams

The final report will include five main UML diagrams:

1. Use Case Diagram
2. Class Diagram
3. Activity Diagram for Automatic Task Allocation
4. Activity Diagram for Template-Based Project Decomposition
5. Sequence Diagram for Delayed Task Reassignment

These diagrams are enough to describe both the general system structure and the complex internal workflows.

---

# 3. Use Case Diagram

## Purpose

The Use Case Diagram shows the main interactions between the users and the system.

It explains what the manager can do and how the system supports project coordination, task allocation, task monitoring, and reassignment.

## Main Actors

### Manager / Team Leader

The manager is the main user of the system.

The manager can:

- create projects;
- add team members;
- manage skills;
- create tasks;
- define required skills;
- preview allocation results;
- automatically allocate tasks;
- generate tasks from project templates;
- reassign delayed tasks;
- view workload analysis;
- view conflict suggestions;
- view notifications.

### Team Member

The team member is the person who receives assigned tasks.

The team member is represented in the system through a structured profile that includes:

- role;
- skills;
- availability;
- workload;
- reliability;
- dynamic status;
- mood state.

### System / Scheduler

The system can also perform automatic checks, such as:

- checking approaching deadlines;
- detecting overdue tasks;
- creating reminder notifications;
- marking overdue tasks as delayed.

## Main Use Cases

The diagram should include:

- Create Project
- Manage Team Members
- Manage Skills
- Create Task
- Add Required Skills
- Preview Task Allocation
- Automatically Allocate Task
- Generate Tasks from Template
- Generate and Allocate Multiple Tasks
- Analyze Workload
- Detect Assignment Conflicts
- Reassign Delayed Task
- Move Task to Manual Review
- View Notifications
- Check Deadlines

## Why This Diagram Is Needed

This diagram gives a high-level view of the system scope. It shows that the application is not limited to CRUD operations, because it also includes automatic allocation, template-based generation, conflict detection, and reassignment.

---

# 4. Class Diagram

## Purpose

The Class Diagram shows the main entities of the system and their relationships.

It describes how projects, team members, skills, tasks, assignments, and notifications are connected.

## Main Classes

The diagram should include these main classes:

### User

Attributes:

- id
- name
- email
- password
- role

### Project

Attributes:

- id
- title
- description
- created_at
- deadline

### TeamMember

Attributes:

- id
- name
- role
- availability
- workload
- reliability
- dynamic_status
- mood_state
- project_id

### Skill

Attributes:

- id
- skill_name
- type
- level

### TeamMemberSkill

Attributes:

- id
- team_member_id
- skill_id

### Task

Attributes:

- id
- title
- description
- priority
- deadline
- status
- estimated_effort
- project_id

### TaskRequiredSkill

Attributes:

- id
- task_id
- skill_id

### Assignment

Attributes:

- id
- task_id
- team_member_id
- assigned_at
- assignment_status

### Notification

Attributes:

- id
- user_id
- message
- type
- is_read
- created_at

## Main Relationships

The diagram should show:

- One Project contains many Tasks.
- One Project contains many TeamMembers.
- One TeamMember can have many Skills.
- One Skill can belong to many TeamMembers.
- One Task can require many Skills.
- One Skill can be required by many Tasks.
- One Task can have many Assignments over time.
- One TeamMember can have many Assignments.
- One User can have many Notifications.

## Why This Diagram Is Needed

This diagram shows the data structure of the system. It is also important because the `TeamMember` class contains detailed profile attributes that are used by the allocation algorithm, not only stored in the database.

---

# 5. Activity Diagram: Automatic Task Allocation

## Purpose

This Activity Diagram describes the workflow used when the system automatically assigns a task to the most suitable team member.

This is one of the main complex functionalities of the project.

## Workflow

The diagram should show the following steps:

1. Manager selects a task for automatic allocation.
2. System retrieves task information.
3. System retrieves required skills.
4. System retrieves team members from the same project.
5. System analyzes each team member profile.
6. System calculates candidate scores using:
   - skill match;
   - taxonomy match;
   - availability;
   - workload;
   - reliability;
   - dynamic status;
   - mood;
   - priority;
   - deadline urgency.
7. System calculates the final weighted score.
8. System sorts candidates by score.
9. System checks whether the best score is above the threshold.
10. If the score is acceptable:
    - create assignment;
    - update task status to assigned;
    - increase selected member workload;
    - create notification.
11. If no candidate is suitable:
    - move task to manual review;
    - create manual review notification.

## Main Decision Points

The diagram should include:

- Are there required skills?
- Are there available candidates?
- Is the best score above the threshold?
- Should the task be assigned or moved to manual review?

## Why This Diagram Is Needed

This diagram proves that automatic task allocation is not a simple database operation. It is a multi-step heuristic workflow based on scoring, constraints, and decision rules.

---

# 6. Activity Diagram: Template-Based Project Decomposition

## Purpose

This Activity Diagram describes how the system generates multiple tasks from a predefined project template.

This workflow supports structured project creation without using AI, ML, or free-text generation.

## Workflow

The diagram should show the following steps:

1. Manager chooses Structured Project mode.
2. Manager selects a project.
3. Manager selects a project template.
4. Manager selects project components.
5. Manager selects complexity for each component.
6. System validates the selected template and components.
7. For each selected component, the system:
   - maps component to task title;
   - maps component to task description;
   - maps component to required skills;
   - maps complexity to priority;
   - maps complexity to estimated effort.
8. System checks duplicate protection.
9. If a duplicate task already exists and duplicates are not allowed:
   - skip task;
   - add it to skipped tasks.
10. If task is not duplicate:
    - create task;
    - create or reuse skills;
    - attach required skills to the task.
11. If generate-and-allocate mode is selected:
    - run automatic allocation for each generated task.
12. System returns:
    - created tasks;
    - skipped tasks;
    - assignment results;
    - scores and explanations;
    - manual review cases.

## Main Decision Points

The diagram should include:

- Is the template valid?
- Is the selected component valid?
- Does the generated task already exist?
- Should the system only generate tasks or also allocate them?
- Is a suitable candidate found?

## Why This Diagram Is Needed

This diagram shows one of the strongest complex features of the project. It combines project decomposition, task generation, required skill mapping, complexity mapping, duplicate prevention, and optional multi-task allocation.

---

# 7. Sequence Diagram: Delayed Task Reassignment

## Purpose

This Sequence Diagram shows how the system reassigns a delayed task to another suitable team member.

This is an important complex workflow because it involves several system components and decision steps.

## Main Participants

The sequence diagram should include:

- Manager
- Assignment Router
- Reassignment Engine
- Database
- Profile Scoring Service
- Notification Service

## Main Sequence

The diagram should show the following interaction:

1. Manager requests reassignment of a delayed task.
2. Assignment Router receives the request.
3. Assignment Router calls Reassignment Engine.
4. Reassignment Engine retrieves the task from the database.
5. Reassignment Engine checks that the task status is delayed.
6. Reassignment Engine finds the current active assignment.
7. Reassignment Engine retrieves team members from the same project.
8. Reassignment Engine excludes the current assignee.
9. Reassignment Engine excludes unavailable members.
10. Reassignment Engine calls Profile Scoring Service.
11. Profile Scoring Service returns candidate scores and explanations.
12. Reassignment Engine selects the best replacement.
13. If replacement is found:
    - old assignment becomes reassigned;
    - previous member workload decreases;
    - new assignment is created;
    - new member workload increases;
    - task status becomes assigned;
    - notification is created.
14. If no replacement is found:
    - task status becomes manual review;
    - manual review notification is created.

## Alternative Flows

The diagram can also show:

- task not found;
- task is not delayed;
- no active assignment exists;
- no suitable replacement is available.

## Why This Diagram Is Needed

This diagram shows that delayed task reassignment is not just a status update. It is a complex workflow that includes assignment history, candidate filtering, scoring, workload updates, and notification creation.

---

# 8. Diagram-to-Requirement Mapping

| Diagram | Main Purpose | Requirement Supported |
|---|---|---|
| Use Case Diagram | Shows main system interactions | General system scope |
| Class Diagram | Shows entities and relationships | DB / data structure |
| Activity Diagram: Automatic Task Allocation | Shows heuristic scoring workflow | Complex functionality |
| Activity Diagram: Template-Based Project Decomposition | Shows structured task generation workflow | Complex functionality |
| Sequence Diagram: Delayed Task Reassignment | Shows reassignment component interaction | Complex functionality |

---

# 9. Conclusion

These five diagrams are sufficient for the current version of the project.

They cover:

- the main users and system use cases;
- the core database structure;
- automatic task allocation;
- structured project decomposition;
- delayed task reassignment.

The most important diagrams for demonstrating algorithmic complexity are:

1. Activity Diagram for Automatic Task Allocation
2. Activity Diagram for Template-Based Project Decomposition
3. Sequence Diagram for Delayed Task Reassignment

Together, they show that the project contains meaningful rule-based application logic beyond simple CRUD functionality.
