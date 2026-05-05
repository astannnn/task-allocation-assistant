# Heuristic Task Allocation Algorithm

## Overview

The Task Allocation Assistant uses a heuristic task-to-member allocation algorithm to support managers in assigning tasks to suitable team members.

The goal of the algorithm is not only to find a person with matching hard skills, but also to evaluate the current project context. The system considers skills, role compatibility, workload, availability, reliability, dynamic status, mood state, task priority, and deadline urgency.

This makes the allocation process more advanced than a simple manual assignment or database query.

## Purpose of the Algorithm

The purpose of the allocation algorithm is to answer the following question:

```text
Given a task with required skills, priority, effort, and deadline,
which team member is currently the most suitable candidate?
```

The system evaluates all team members in the same project and calculates a score for each candidate. The candidate with the highest acceptable score is selected.

If no candidate reaches the minimum acceptable score, the task is not assigned automatically and is moved to manual review.

## Why This Is a Complex Functionality

This functionality is considered algorithmically complex because the main value lies in the internal decision-making logic.

The algorithm performs:

- multi-criteria candidate evaluation;
- skill matching;
- taxonomy and role compatibility analysis;
- workload-aware decision-making;
- availability evaluation;
- reliability evaluation;
- dynamic status evaluation;
- mood state evaluation;
- priority-based scoring;
- deadline urgency scoring;
- explainable ranking of candidates;
- automatic assignment or manual review fallback.

This goes beyond simple CRUD operations because the system does not only store and retrieve tasks. It analyzes structured data and makes a decision based on weighted heuristics.

## Input Data

The algorithm uses data from several system entities.

### Task Data

```text
title
description
priority
deadline
status
estimated_effort
required_skills
```

### Team Member Profile Data

```text
name
role
availability
workload
reliability
dynamic_status
mood_state
skills
```

### Skill and Taxonomy Data

```text
skill name
skill type
skill category
team member skill level
required skill level
role ontology
skill taxonomy
```

## Scoring Criteria

Each candidate is evaluated using the following criteria.

### 1. Skill Match

The system checks whether the team member has the skills required by the task.

Example:

```text
Task required skills:
Python, FastAPI, API Design

Team member skills:
Python, FastAPI, Problem Solving
```

In this case, the member has a partial match.

### 2. Taxonomy Match

The system uses a predefined taxonomy of skill categories and role ontology.

Example:

```text
Backend Developer
→ backend_development
→ soft_skills
```

If the task requires backend-related skills and the member role belongs to backend development, the taxonomy score increases.

### 3. Availability

The system checks whether the team member is currently available.

```text
availability = 0.0 means not available
availability = 1.0 means fully available
```

### 4. Workload Score

The system checks the current workload of the team member.

```text
low workload → better score
high workload → lower score
```

This helps prevent overloading one person.

### 5. Reliability

Reliability represents how dependable the team member is for completing assigned work.

```text
higher reliability → better score
```

### 6. Dynamic Status

The system considers the current work state of the member.

Example statuses:

```text
normal
busy
tired
unavailable
```

Unavailable members are not suitable candidates.

### 7. Mood State

The system considers selected mood or engagement indicators.

Example states:

```text
positive
neutral
stressed
```

This does not dominate the final decision, but it slightly affects the score.

### 8. Priority Score

High-priority and critical tasks increase the importance of selecting a suitable candidate.

Example:

```text
low → lower priority score
medium → normal priority score
high → high priority score
critical → maximum priority score
```

### 9. Deadline Urgency Score

Tasks with approaching deadlines receive urgency consideration.

This helps the system prioritize urgent tasks and avoid late project execution.

## Weighted Scoring Formula

The current scoring formula is:

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

The weights reflect the importance of each factor.

Skill match has the highest weight because the team member must be technically capable of completing the task. Availability and workload are also important because the system should avoid assigning tasks to overloaded members.

Mood has a smaller weight because it is useful contextual information but should not dominate the decision.

## Minimum Acceptable Score

The system uses a threshold:

```text
MINIMUM_ACCEPTABLE_SCORE = 0.5
```

If the best candidate has a score greater than or equal to this threshold, the task can be assigned automatically.

If the best candidate has a score below the threshold, the task is moved to manual review.

This prevents the system from assigning tasks to unsuitable candidates.

## Algorithm Workflow

```text
1. Receive task_id.
2. Retrieve the task from the database.
3. Retrieve required skills for the task.
4. Retrieve all team members in the same project.
5. For each team member:
   5.1 Calculate skill match.
   5.2 Calculate taxonomy match.
   5.3 Calculate availability score.
   5.4 Calculate workload score.
   5.5 Calculate reliability score.
   5.6 Calculate dynamic status score.
   5.7 Calculate mood score.
   5.8 Calculate priority score.
   5.9 Calculate deadline urgency score.
   5.10 Calculate final weighted score.
   5.11 Generate explanation.
6. Sort candidates by final score.
7. Select the best candidate.
8. If best candidate score is below threshold:
   8.1 Move task to manual review.
   8.2 Create manual review notification.
9. If best candidate score is acceptable:
   9.1 Close previous active assignments for this task.
   9.2 Create new active assignment.
   9.3 Update task status to assigned.
   9.4 Increase selected member workload.
   9.5 Create assignment notification.
10. Return assignment result, candidate scores, score breakdown, and explanation.
```

## Manual Review Fallback

The system does not force an automatic assignment when the candidate quality is too low.

Example:

```text
Task: Design database schema
Required skills: SQL, Database Design

Best candidate score: 0.485
Threshold: 0.5
```

Since the candidate score is below the threshold, the system moves the task to manual review.

This is important because the system is a decision-support assistant, not a fully autonomous manager.

## One Active Assignment Rule

The system also enforces the business rule:

```text
one task should have only one active assignment at a time
```

Before creating a new active assignment, the system closes previous active assignments by changing their status to:

```text
reassigned
```

Then it creates a new assignment with status:

```text
active
```

This keeps assignment history while preventing inconsistent data.

## Explainability

The algorithm returns a detailed explanation for each candidate.

Example explanation:

```text
Ali received a final score of 0.695 for task 'Develop backend API'.
Positive factors: partial match with the required skills, strong role-task taxonomy compatibility,
high task priority, high availability, high reliability, good dynamic status, positive mood state.
Risk factors: high current workload.
```

This makes the system more transparent for the manager.

The manager can understand:

- why a person was selected;
- why another person was rejected;
- which factors improved the score;
- which factors reduced the score.

## Candidate Score Breakdown

For each candidate, the system returns a score breakdown.

Example:

```json
{
  "skill_match": 0.6667,
  "taxonomy_match": 1,
  "availability": 0.9,
  "workload_score": 0,
  "reliability": 0.85,
  "dynamic_status_score": 1,
  "mood_score": 1,
  "priority_score": 1,
  "deadline_urgency_score": 0.5,
  "final_score": 0.695
}
```

This breakdown is useful for debugging, testing, and explaining the system behavior in the final report.

## Related Files

```text
app/services/profile_scoring.py
app/services/allocation_engine.py
app/services/taxonomy.py
app/services/notification_service.py
tests/test_profile_scoring.py
tests/test_allocation_engine.py
```

## Related Endpoints

```http
GET /assignments/preview/{task_id}
```

Returns candidate ranking and explanations without creating an assignment.

```http
POST /assignments/auto-allocate/{task_id}
```

Automatically assigns a task to the best suitable team member if the score is acceptable.

```http
POST /project-templates/projects/{project_id}/generate-and-allocate
```

Generates multiple tasks from a project template and runs the allocation algorithm for each generated task.

## Testing

The allocation logic is covered by tests for:

```text
strongest candidate selection
candidate score sorting
candidate explanation and breakdown
minimum threshold behavior
task not found case
closing previous active assignments
one active assignment rule
```

Current test status:

```text
36 passed
```

## Summary

The heuristic task allocation algorithm is one of the core complex functionalities of the project.

It supports intelligent task assignment by combining structured team-member profiles, skill taxonomy, workload balancing, priority, deadline urgency, and explainable scoring.

This functionality directly addresses the Software Engineering project requirement for complex application logic mostly implemented by the student.