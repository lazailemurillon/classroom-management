
from celery import shared_task
from .models import Student, Activity, ActivityScore, TopStudent
from django.contrib.auth.models import User


@shared_task
def compute_top_students(user_id):

    user = User.objects.get(id=user_id)

    # delete old rankings
    TopStudent.objects.filter(user=user).delete()

    students = Student.objects.filter(classroom__user=user)

    results = []

    for student in students:

        activities = Activity.objects.filter(
            classroom=student.classroom
        )

        total_score = 0
        total_points = 0

        incomplete = False

        for act in activities:

            score_obj = ActivityScore.objects.filter(
                activity=act,
                student=student
            ).first()

            if not score_obj or score_obj.score is None:
                incomplete = True
                break

            total_score += score_obj.score
            total_points += act.points

        if incomplete:
            continue

        if total_points > 0:

            average = (total_score / total_points) * 100

            results.append({
                "student": student,
                "average": average
            })

    # sort descending
    results.sort(key=lambda x: x["average"], reverse=True)

    # save top 10
    for item in results[:10]:

        TopStudent.objects.create(
            user=user,
            student=item["student"],
            average=item["average"]
        )

    return "done"
