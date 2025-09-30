from django import template

register = template.Library()

@register.filter
def percentage(student_list, max_percentage):

    count = 0
    for student in student_list:
        if max_percentage == 0:
            if student['progress_percentage'] == 0:
                count += 1
        elif max_percentage == 100:
            if student['progress_percentage'] == 100:
                count += 1
        else:
            if 0 < student['progress_percentage'] <= max_percentage:
                count += 1
    return count