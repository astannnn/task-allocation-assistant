# Testing Plan

## 1. Purpose of Testing

The purpose of testing in this project is to verify that the main backend functionalities work correctly and that the complex task allocation logic behaves as expected.

The testing process focuses not only on simple CRUD behavior, but also on the internal decision-support logic of the system, including profile scoring, automatic allocation, reassignment, template-based task generation, deadline checking, and notifications.

---

## 2. Testing Approach

The project uses automated unit tests with `pytest`.

The tests are focused on service-level logic because the most important part of the project is implemented in backend services such as:

- profile scoring service;
- allocation engine;
- reassignment engine;
- project template service;
- reminder service;
- notification service.

This approach makes it possible to test the internal logic of the system independently from the user interface.

---

## 3. Testing Tool

The project uses:

```text
Pytest
```

To run all tests:

```bash
PYTHONPATH=. pytest
```

Current test result:

```text
49 passed
```

---

## 4. Tested Components

### 4.1 Profile Scoring Tests

Test file:

```text
tests/test_profile_scoring.py
```

This test file verifies the scoring logic used to evaluate team members.

Tested aspects include:

- skill match score;
- availability score;
- workload score;
- reliability score;
- dynamic status score;
- mood score;
- taxonomy match score;
- priority score;
- deadline urgency score;
- final score breakdown fields.

These tests are important because profile scoring is the foundation of the automatic task allocation logic.

---

### 4.2 Allocation Engine Tests

Test file:

```text
tests/test_allocation_engine.py
```

This test file verifies the automatic task allocation logic.

Tested aspects include:

- strongest candidate selection;
- candidate score sorting;
- candidate response structure;
- explanation and score breakdown;
- weak candidate below threshold;
- task not found behavior;
- closing previous active assignments;
- one active assignment rule.

These tests are important because automatic allocation is one of the main algorithmically complex functionalities of the project.

---

### 4.3 Reassignment Engine Tests

Test file:

```text
tests/test_reassignment_engine.py
```

This test file verifies the delayed task reassignment logic.

Tested aspects include:

- finding the current active assignment;
- excluding the current assignee from replacement candidates;
- excluding unavailable members;
- sorting replacement candidates by score;
- returning explanation and score breakdown;
- task not found behavior.

These tests are important because delayed task reassignment is a multi-step workflow involving task status, assignments, candidate filtering, scoring, and workload updates.

---

### 4.4 Project Template Service Tests

Test file:

```text
tests/test_project_template_service.py
```

This test file verifies the template-based project decomposition logic.

Tested aspects include:

- available templates;
- website development template structure;
- expected template components;
- complexity mapping;
- invalid complexity handling;
- generated task titles;
- generated required skills;
- invalid template handling;
- invalid component handling;
- decomposition summary.

These tests are important because template-based decomposition is one of the strongest complex functionalities of the project.

---

### 4.5 Project Template Router Logic Tests

Test file:

```text
tests/test_project_template_router_logic.py
```

This test file verifies router-level behavior related to project template task generation.

Tested aspects include:

- duplicate template tasks are skipped by default;
- duplicate task generation is allowed when `allow_duplicates=True`.

These tests are important because duplicate protection is part of the business logic of structured project creation.

---

### 4.6 Reminder Service Tests

Test file:

```text
tests/test_reminder_service.py
```

This test file verifies the deadline reminder and overdue task detection workflow.

Tested aspects include:

- approaching deadline creates a deadline reminder;
- overdue task becomes delayed;
- duplicate deadline reminders are not created;
- completed tasks are ignored by deadline checks.

These tests are important because deadline checking supports the notification workflow and helps the manager identify tasks that require attention.

---

### 4.7 Notification Service Tests

Test file:

```text
tests/test_notification_service.py
```

This test file verifies the notification service.

Tested aspects include:

- creating a notification;
- retrieving all notifications;
- retrieving notifications by user;
- marking a notification as read;
- returning `None` for missing notifications;
- creating task assignment notifications;
- creating task reassignment notifications;
- creating reassignment notifications without previous assignee;
- creating manual review notifications.

These tests are important because notifications are used across different workflows, including automatic assignment, reassignment, manual review, and deadline reminders.

---

## 5. Complex Functionality Testing

The most important testing focus is on the complex functionalities of the project.

The following complex workflows are covered by automated tests:

1. Multi-criteria profile scoring
2. Automatic task allocation
3. Delayed task reassignment
4. Template-based project decomposition
5. Duplicate task prevention
6. Deadline reminder workflow
7. Overdue task detection
8. Notification generation

This demonstrates that the project contains application logic beyond simple CRUD operations.

---

## 6. Test Database Strategy

Some tests use isolated in-memory SQLite databases.

This allows tests to run without depending on the real local project database file.

Benefits:

- tests are isolated;
- tests do not modify production or development data;
- tests are repeatable;
- database state is recreated for each test session.

---

## 7. Manual Testing

In addition to automated tests, some workflows can be tested manually through Swagger UI.

Swagger URL:

```text
http://127.0.0.1:8000/docs
```

Manual testing can be used for:

- creating projects;
- adding team members;
- adding skills;
- creating tasks;
- adding required skills;
- previewing task allocation;
- running automatic allocation;
- generating template-based tasks;
- generating and allocating multiple tasks;
- checking workload analytics;
- checking conflict suggestions;
- running manual deadline check;
- viewing notifications.

---

## 8. Example Manual Test Scenario

A typical manual test scenario is:

1. Create a project.
2. Add several team members with different roles, skills, workload, availability, reliability, dynamic status, and mood.
3. Create a task with required skills.
4. Run allocation preview.
5. Check candidate scores and explanations.
6. Run automatic allocation.
7. Verify that an assignment is created.
8. Verify that the task status becomes assigned.
9. Verify that the selected member workload increases.
10. Verify that a notification is created.

This scenario validates the main task allocation workflow.

---

## 9. Template-Based Manual Test Scenario

A template-based manual test scenario is:

1. Create a project.
2. Add team members with different profiles and skills.
3. Select the `website_development` template.
4. Select project components such as backend API, frontend pages, database design, authentication, testing, and documentation.
5. Select complexity for each component.
6. Run generate-and-allocate.
7. Verify that multiple tasks are created.
8. Verify that required skills are assigned to tasks.
9. Verify that each task is allocated or moved to manual review.
10. Verify that the response includes scores and explanations.

This scenario validates the structured project / multi-task allocation workflow.

---

## 10. Expected Test Result

The current expected result is:

```text
49 passed
```

This means that all currently implemented automated tests pass successfully.

---

## 11. Future Testing Improvements

Possible future improvements include:

- API endpoint tests using FastAPI TestClient;
- CRUD endpoint tests;
- integration tests for complete allocation workflows;
- tests for workload analytics endpoints;
- tests for conflict detection endpoints;
- tests for scheduler startup and shutdown behavior;
- frontend interaction tests if a user interface is implemented.

---

## 12. Conclusion

The testing strategy confirms that the project is not limited to basic CRUD operations. The automated tests cover the main decision-support logic of the system, including scoring, allocation, reassignment, reminders, notifications, and template-based task generation.

This supports the Software Engineering requirement that complex functionalities must be implemented and validated through clear application logic.
