from django import template

register = template.Library()


@register.filter
def in_category(projects, status):
    return projects.filter(status=status)


@register.filter
def find_comments(comments, project_id):
    return comments.filter(project_id=project_id)