import pytest

from app.services.project_template_service import (
    get_available_project_templates,
    map_complexity_to_task_attributes,
    generate_tasks_from_template,
    generate_project_decomposition_summary,
)


def test_available_templates_include_website_development():
    templates = get_available_project_templates()

    template_keys = [template["template_key"] for template in templates]

    assert "website_development" in template_keys


def test_website_template_contains_expected_components():
    templates = get_available_project_templates()

    website_template = next(
        template
        for template in templates
        if template["template_key"] == "website_development"
    )

    component_keys = [
        component["component_key"]
        for component in website_template["components"]
    ]

    assert "backend_api" in component_keys
    assert "frontend_pages" in component_keys
    assert "database_design" in component_keys
    assert "authentication" in component_keys
    assert "testing" in component_keys


def test_complexity_low_maps_to_medium_priority_and_low_effort():
    result = map_complexity_to_task_attributes("low")

    assert result["priority"] == "medium"
    assert result["estimated_effort"] == 0.2


def test_complexity_medium_maps_to_high_priority_and_medium_effort():
    result = map_complexity_to_task_attributes("medium")

    assert result["priority"] == "high"
    assert result["estimated_effort"] == 0.3


def test_complexity_high_maps_to_critical_priority_and_high_effort():
    result = map_complexity_to_task_attributes("high")

    assert result["priority"] == "critical"
    assert result["estimated_effort"] == 0.4


def test_invalid_complexity_raises_error():
    with pytest.raises(ValueError):
        map_complexity_to_task_attributes("very_high")


def test_generate_tasks_from_template_creates_expected_task_titles():
    selected_components = [
        {
            "component_key": "backend_api",
            "complexity": "high",
        },
        {
            "component_key": "frontend_pages",
            "complexity": "medium",
        },
    ]

    generated_tasks = generate_tasks_from_template(
        template_key="website_development",
        selected_components=selected_components,
    )

    task_titles = [task["title"] for task in generated_tasks]

    assert len(generated_tasks) == 2
    assert "Develop backend API" in task_titles
    assert "Build frontend pages" in task_titles


def test_generate_tasks_from_template_assigns_required_skills():
    selected_components = [
        {
            "component_key": "backend_api",
            "complexity": "high",
        },
        {
            "component_key": "database_design",
            "complexity": "medium",
        },
    ]

    generated_tasks = generate_tasks_from_template(
        template_key="website_development",
        selected_components=selected_components,
    )

    backend_task = generated_tasks[0]
    database_task = generated_tasks[1]

    assert backend_task["required_skills"] == ["Python", "FastAPI", "API Design"]
    assert database_task["required_skills"] == ["SQL", "Database Design"]


def test_generate_tasks_from_template_maps_complexity_to_priority_and_effort():
    selected_components = [
        {
            "component_key": "authentication",
            "complexity": "high",
        },
        {
            "component_key": "testing",
            "complexity": "low",
        },
    ]

    generated_tasks = generate_tasks_from_template(
        template_key="website_development",
        selected_components=selected_components,
    )

    authentication_task = generated_tasks[0]
    testing_task = generated_tasks[1]

    assert authentication_task["priority"] == "critical"
    assert authentication_task["estimated_effort"] == 0.4

    assert testing_task["priority"] == "medium"
    assert testing_task["estimated_effort"] == 0.2


def test_invalid_template_raises_error():
    selected_components = [
        {
            "component_key": "backend_api",
            "complexity": "high",
        }
    ]

    with pytest.raises(ValueError):
        generate_tasks_from_template(
            template_key="mobile_app_development",
            selected_components=selected_components,
        )


def test_invalid_component_raises_error():
    selected_components = [
        {
            "component_key": "payment_system",
            "complexity": "high",
        }
    ]

    with pytest.raises(ValueError):
        generate_tasks_from_template(
            template_key="website_development",
            selected_components=selected_components,
        )


def test_project_decomposition_summary_contains_generated_tasks():
    selected_components = [
        {
            "component_key": "backend_api",
            "complexity": "high",
        },
        {
            "component_key": "documentation",
            "complexity": "low",
        },
    ]

    summary = generate_project_decomposition_summary(
        template_key="website_development",
        selected_components=selected_components,
    )

    assert summary["template_key"] == "website_development"
    assert summary["template_name"] == "Website Development"
    assert summary["total_generated_tasks"] == 2
    assert len(summary["generated_tasks"]) == 2