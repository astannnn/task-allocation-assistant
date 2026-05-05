# Template-Based Project Decomposition and Multi-Task Allocation

## Overview

Template-Based Project Decomposition is a complex functionality of the Task Allocation Assistant for Team and Project Management.

The purpose of this feature is to allow a manager to create not only a single task, but also a structured project composed of several predefined components. Instead of writing a free-text prompt or using generative AI, the manager selects a project template, chooses the required components, and assigns a complexity level to each component.

The system then automatically generates project tasks, assigns required skills to each task, maps complexity to priority and estimated effort, and can optionally run the allocation algorithm for every generated task.

## Why This Is a Complex Functionality

This feature is considered algorithmically complex because it is not a simple CRUD operation. The system does not only store data in the database; it performs a structured workflow that transforms high-level project choices into concrete tasks and allocation decisions.

The functionality includes:

- structured project decomposition;
- mapping project components to required skills;
- mapping complexity levels to task priority and estimated effort;
- automatic generation of multiple tasks;
- automatic creation or reuse of required skills;
- optional multi-task allocation using the existing heuristic scoring algorithm;
- workload-aware assignment;
- explainable candidate scoring for every generated task;
- manual review when no candidate reaches the minimum acceptable score;
- duplicate protection to avoid creating the same template task multiple times.

This makes the feature suitable for the complex functionality category required in the Software Engineering project.

## Supported Project Template

Currently, the system supports the following template:

```text
Website Development
```

Available components:

```text
Backend API
Frontend Pages
Database Design
Authentication
Admin Panel
Testing
Documentation
```

Example mapping:

```text
Backend API
→ Develop backend API
→ Required skills: Python, FastAPI, API Design

Frontend Pages
→ Build frontend pages
→ Required skills: JavaScript, HTML, CSS, UI Design

Database Design
→ Design database schema
→ Required skills: SQL, Database Design

Authentication
→ Implement authentication
→ Required skills: Python, FastAPI, Authentication

Testing
→ Test website functionality
→ Required skills: Problem Solving, Communication
```

## Complexity Mapping

The manager selects a complexity level for each component.

```text
low
→ priority: medium
→ estimated_effort: 0.2

medium
→ priority: high
→ estimated_effort: 0.3

high
→ priority: critical
→ estimated_effort: 0.4
```

## Main Workflow

```text
1. Manager selects a project template.
2. Manager selects project components.
3. Manager chooses complexity for each component.
4. System validates the selected template and components.
5. System generates task definitions.
6. System maps each component to required skills.
7. System maps complexity to priority and estimated effort.
8. System creates tasks in the database.
9. System creates or reuses required skills.
10. System links required skills to generated tasks.
11. If generate-and-allocate is used, the system runs the allocation algorithm for each task.
12. If a suitable candidate is found, the task is assigned.
13. If no suitable candidate is found, the task is moved to manual review.
```

## API Endpoints

### Get Available Templates

```http
GET /project-templates/
```

Returns all available project templates, components, required skills, and allowed complexity levels.

### Generate Task Preview

```http
POST /project-templates/generate-tasks
```

Generates task definitions from the selected template, but does not save them in the database.

### Generate Decomposition Summary

```http
POST /project-templates/generate-summary
```

Returns a structured summary of generated tasks, required skills, priorities, and estimated efforts.

### Generate Template Tasks for a Project

```http
POST /project-templates/projects/{project_id}/generate-template-tasks
```

Creates generated tasks in the database for a selected project.

This endpoint also:

- creates missing skills;
- links required skills to tasks;
- prevents duplicate task creation by default;
- returns created and skipped tasks.

### Generate and Allocate

```http
POST /project-templates/projects/{project_id}/generate-and-allocate
```

Creates generated tasks and immediately runs the automatic allocation algorithm for each generated task.

The response includes:

- created task information;
- required skills;
- allocation result;
- selected team member;
- score at assignment;
- candidate score breakdown;
- explanation;
- manual review result if no candidate passes the threshold.

## Example Request

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
      "complexity": "medium"
    },
    {
      "component_key": "authentication",
      "complexity": "high"
    },
    {
      "component_key": "testing",
      "complexity": "low"
    }
  ]
}
```

## Example Generated Tasks

The system can generate the following tasks:

```text
Develop backend API
→ required skills: Python, FastAPI, API Design
→ priority: critical
→ estimated effort: 0.4

Build frontend pages
→ required skills: JavaScript, HTML, CSS, UI Design
→ priority: high
→ estimated effort: 0.3

Design database schema
→ required skills: SQL, Database Design
→ priority: high
→ estimated effort: 0.3

Implement authentication
→ required skills: Python, FastAPI, Authentication
→ priority: critical
→ estimated effort: 0.4

Test website functionality
→ required skills: Problem Solving, Communication
→ priority: medium
→ estimated effort: 0.2
```

When using generate-and-allocate, the system also evaluates team members and assigns suitable candidates. If no team member reaches the minimum acceptable score, the task is moved to manual review.

## Example Allocation Result

Example allocation summary after running `generate-and-allocate`:

```text
Develop backend API
→ assigned to Backend Developer
→ score: 0.695
→ explanation includes skill match, taxonomy match, availability, workload, reliability, dynamic status, mood, priority, and deadline urgency

Build frontend pages
→ assigned to Frontend Developer
→ score: 0.601
→ explanation includes frontend taxonomy compatibility and candidate profile evaluation

Design database schema
→ moved to manual review
→ reason: no candidate reached the minimum acceptable score

Implement authentication
→ assigned to Backend Developer
→ score: 0.695

Test website functionality
→ assigned to suitable available team member
→ score: 0.625
```

## Duplicate Protection

By default, duplicate tasks are not created.

If a generated task already exists in the selected project, the system skips it and returns it in `skipped_tasks`.

Example result:

```json
{
  "total_created_tasks": 0,
  "total_skipped_tasks": 2,
  "skipped_tasks": [
    {
      "title": "Develop backend API",
      "reason": "Task already exists in this project"
    }
  ]
}
```

If duplicates are intentionally needed, the manager can set:

```json
{
  "allow_duplicates": true
}
```

## Relation to Professor Requirements

This feature directly supports the requirement that the project should include complex functionalities mostly implemented by the student.

It combines:

- rule-based project decomposition;
- predefined project templates;
- skill taxonomy usage;
- task generation logic;
- required skill mapping;
- heuristic task allocation;
- workload-aware scoring;
- explainable decision-making;
- manual review fallback.

Therefore, it is not only a third-party or CRUD functionality. It is a complex workflow implemented inside the application logic.

## Relation to Other Complex Functionalities

This feature is connected with the existing complex logic of the system:

```text
Project template decomposition
→ generated task definitions
→ required skill mapping
→ profile scoring
→ taxonomy matching
→ workload-aware allocation
→ explainable assignment
→ manual review when needed
```

It uses the existing allocation engine instead of replacing it. This means that the project-level feature is built on top of the single-task allocation logic and extends it to multi-task project creation.

## Related Files

```text
app/services/project_template_service.py
app/routers/project_templates.py
app/services/allocation_engine.py
tests/test_project_template_service.py
tests/test_project_template_router_logic.py
tests/test_allocation_engine.py
```

## Testing

This feature is covered by tests for:

```text
available templates
expected template components
complexity mapping
generated task titles
required skill mapping
invalid template handling
invalid component handling
decomposition summary
duplicate protection
allow_duplicates behavior
automatic allocation active assignment rule
```

Current test status:

```text
36 passed
```

## Summary

Template-Based Project Decomposition and Multi-Task Allocation transforms the system from a simple task tracker into a more intelligent project management assistant.

The manager can define a structured project through predefined options, and the system can automatically generate tasks, determine required skills, estimate task effort, assign priority, allocate tasks to suitable team members, and explain the allocation result.

This functionality strengthens the project because it demonstrates a complex, rule-based workflow implemented inside the application logic.
