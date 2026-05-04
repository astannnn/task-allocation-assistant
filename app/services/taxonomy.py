"""
Taxonomy and ontology module for the Task Allocation Assistant.

This module defines structured categories of skills and roles.
It is used by the allocation logic to reason about compatibility
between task requirements and team-member profiles.

This is part of the algorithmically complex functionality of the project,
because task allocation is not based only on simple CRUD data, but also on
structured classification of skills, roles, and task requirements.
"""

from typing import Dict, List, Optional


# Main skill taxonomy.
# Each category contains skills that belong to a specific professional area.
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "backend_development": [
        "python",
        "fastapi",
        "django",
        "flask",
        "sql",
        "postgresql",
        "sqlite",
        "api design",
        "database design",
        "authentication",
    ],
    "frontend_development": [
        "javascript",
        "typescript",
        "html",
        "css",
        "react",
        "vue",
        "ui design",
        "responsive design",
    ],
    "data_analysis": [
        "python",
        "sql",
        "excel",
        "power bi",
        "pandas",
        "numpy",
        "data visualization",
        "statistics",
    ],
    "project_management": [
        "planning",
        "coordination",
        "documentation",
        "reporting",
        "risk management",
        "time management",
    ],
    "soft_skills": [
        "communication",
        "problem solving",
        "teamwork",
        "responsibility",
        "leadership",
        "adaptability",
        "critical thinking",
    ],
}


# Role ontology.
# Each role is connected to the categories that are usually important for it.
ROLE_ONTOLOGY: Dict[str, List[str]] = {
    "backend developer": [
        "backend_development",
        "soft_skills",
    ],
    "frontend developer": [
        "frontend_development",
        "soft_skills",
    ],
    "full stack developer": [
        "backend_development",
        "frontend_development",
        "soft_skills",
    ],
    "data analyst": [
        "data_analysis",
        "soft_skills",
    ],
    "project manager": [
        "project_management",
        "soft_skills",
    ],
}


def normalize_text(value: Optional[str]) -> str:
    """
    Normalize text values for comparison.
    Example: 'FastAPI' -> 'fastapi'
    """
    if value is None:
        return ""
    return value.strip().lower()


def get_skill_category(skill_name: str) -> Optional[str]:
    """
    Return the taxonomy category for a given skill.

    Example:
    get_skill_category("Python") -> "backend_development"
    get_skill_category("Communication") -> "soft_skills"
    """
    normalized_skill = normalize_text(skill_name)

    for category, skills in SKILL_TAXONOMY.items():
        if normalized_skill in skills:
            return category

    return None


def get_role_categories(role: str) -> List[str]:
    """
    Return the ontology categories connected to a role.

    Example:
    get_role_categories("Backend Developer")
    -> ["backend_development", "soft_skills"]
    """
    normalized_role = normalize_text(role)
    return ROLE_ONTOLOGY.get(normalized_role, [])


def classify_skills_by_category(skill_names: List[str]) -> Dict[str, List[str]]:
    """
    Group a list of skills by taxonomy category.

    Example:
    ["Python", "FastAPI", "Communication"]
    ->
    {
        "backend_development": ["Python", "FastAPI"],
        "soft_skills": ["Communication"],
        "unknown": []
    }
    """
    result: Dict[str, List[str]] = {}

    for skill_name in skill_names:
        category = get_skill_category(skill_name)

        if category is None:
            category = "unknown"

        if category not in result:
            result[category] = []

        result[category].append(skill_name)

    return result


def calculate_role_skill_compatibility(role: str, skill_names: List[str]) -> float:
    """
    Calculate how compatible a team member's skills are with their role.

    The score is based on how many of the member's skills belong to categories
    expected for their role.

    Score range:
    0.0 = no compatibility
    1.0 = high compatibility
    """
    if not skill_names:
        return 0.0

    role_categories = get_role_categories(role)

    if not role_categories:
        return 0.5

    compatible_count = 0

    for skill_name in skill_names:
        skill_category = get_skill_category(skill_name)

        if skill_category in role_categories:
            compatible_count += 1

    return round(compatible_count / len(skill_names), 4)


def calculate_task_category_match(
    task_required_skills: List[str],
    member_role: str,
) -> float:
    """
    Calculate how well a member's role matches the categories required by a task.

    Example:
    Task requires Python and FastAPI.
    Member role is Backend Developer.
    Result should be high because backend developers are compatible
    with backend_development skills.
    """
    if not task_required_skills:
        return 0.0

    role_categories = get_role_categories(member_role)

    if not role_categories:
        return 0.5

    matched_count = 0

    for skill_name in task_required_skills:
        skill_category = get_skill_category(skill_name)

        if skill_category in role_categories:
            matched_count += 1

    return round(matched_count / len(task_required_skills), 4)


def explain_taxonomy_match(
    task_required_skills: List[str],
    member_role: str,
    member_skills: List[str],
) -> str:
    """
    Create a human-readable explanation of the taxonomy-based match.

    This is useful for explainable task allocation.
    """
    task_categories = classify_skills_by_category(task_required_skills)
    member_categories = classify_skills_by_category(member_skills)
    role_categories = get_role_categories(member_role)

    return (
        f"Task required skills belong to these categories: {task_categories}. "
        f"The team member role '{member_role}' is connected to: {role_categories}. "
        f"The member's skills are classified as: {member_categories}."
    )


def get_taxonomy_summary() -> Dict[str, Dict[str, List[str]]]:
    """
    Return the full taxonomy and ontology structure.
    This can be used in API endpoints, documentation, or testing.
    """
    return {
        "skill_taxonomy": SKILL_TAXONOMY,
        "role_ontology": ROLE_ONTOLOGY,
    }