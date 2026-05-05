PROJECT_TEMPLATES = {
    "website_development": {
        "name": "Website Development",
        "description": "Template for decomposing a website development project into structured tasks.",
        "components": {
            "backend_api": {
                "title": "Develop backend API",
                "description": "Design and implement backend API endpoints for the website.",
                "required_skills": ["Python", "FastAPI", "API Design"],
            },
            "frontend_pages": {
                "title": "Build frontend pages",
                "description": "Create user interface pages for the website.",
                "required_skills": ["JavaScript", "HTML", "CSS", "UI Design"],
            },
            "database_design": {
                "title": "Design database schema",
                "description": "Design the relational database schema for storing project data.",
                "required_skills": ["SQL", "Database Design"],
            },
            "authentication": {
                "title": "Implement authentication",
                "description": "Implement user login, registration, and authentication logic.",
                "required_skills": ["Python", "FastAPI", "Authentication"],
            },
            "admin_panel": {
                "title": "Create admin panel",
                "description": "Create an admin interface for managing users, tasks, and project data.",
                "required_skills": ["Python", "FastAPI", "JavaScript", "UI Design"],
            },
            "testing": {
                "title": "Test website functionality",
                "description": "Test the main website functionality and report discovered issues.",
                "required_skills": ["Problem Solving", "Communication"],
            },
            "documentation": {
                "title": "Write project documentation",
                "description": "Prepare technical and user documentation for the project.",
                "required_skills": ["Documentation", "Communication"],
            },
        },
    }
}


COMPLEXITY_MAPPING = {
    "low": {
        "priority": "medium",
        "estimated_effort": 0.2,
    },
    "medium": {
        "priority": "high",
        "estimated_effort": 0.3,
    },
    "high": {
        "priority": "critical",
        "estimated_effort": 0.4,
    },
}


def get_available_project_templates():
    """
    Return available project templates.

    This function is used by the manager interface to show predefined
    project types and their available components.
    """
    templates = []

    for template_key, template_data in PROJECT_TEMPLATES.items():
        components = []

        for component_key, component_data in template_data["components"].items():
            components.append(
                {
                    "component_key": component_key,
                    "title": component_data["title"],
                    "description": component_data["description"],
                    "required_skills": component_data["required_skills"],
                }
            )

        templates.append(
            {
                "template_key": template_key,
                "name": template_data["name"],
                "description": template_data["description"],
                "components": components,
                "allowed_complexities": list(COMPLEXITY_MAPPING.keys()),
            }
        )

    return templates


def map_complexity_to_task_attributes(complexity: str):
    """
    Convert selected component complexity into task priority and effort.

    This is part of the rule-based project decomposition logic.
    """
    if complexity not in COMPLEXITY_MAPPING:
        raise ValueError(f"Invalid complexity: {complexity}")

    return COMPLEXITY_MAPPING[complexity]


def generate_tasks_from_template(template_key: str, selected_components: list):
    """
    Generate task definitions from a predefined project template.

    The manager does not write a free-text AI prompt. Instead, the manager
    selects project components and complexity levels from predefined options.

    Example selected_components:
    [
        {"component_key": "backend_api", "complexity": "high"},
        {"component_key": "frontend_pages", "complexity": "medium"}
    ]
    """
    if template_key not in PROJECT_TEMPLATES:
        raise ValueError(f"Invalid project template: {template_key}")

    template = PROJECT_TEMPLATES[template_key]
    generated_tasks = []

    for selected_component in selected_components:
        component_key = selected_component.get("component_key")
        complexity = selected_component.get("complexity")

        if component_key not in template["components"]:
            raise ValueError(f"Invalid component for template '{template_key}': {component_key}")

        task_attributes = map_complexity_to_task_attributes(complexity)
        component_data = template["components"][component_key]

        generated_tasks.append(
            {
                "component_key": component_key,
                "title": component_data["title"],
                "description": component_data["description"],
                "required_skills": component_data["required_skills"],
                "complexity": complexity,
                "priority": task_attributes["priority"],
                "estimated_effort": task_attributes["estimated_effort"],
            }
        )

    return generated_tasks


def generate_project_decomposition_summary(template_key: str, selected_components: list):
    """
    Generate a structured summary of the project decomposition result.

    This is useful for API responses and for explaining the complex workflow
    in the final Software Engineering report.
    """
    generated_tasks = generate_tasks_from_template(
        template_key=template_key,
        selected_components=selected_components,
    )

    return {
        "template_key": template_key,
        "template_name": PROJECT_TEMPLATES[template_key]["name"],
        "total_generated_tasks": len(generated_tasks),
        "generated_tasks": generated_tasks,
    }