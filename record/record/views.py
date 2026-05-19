@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')
#total students/ class
@login_required(login_url='login')
def dashboard_stats(request):
    total_classes = ClassRoom.objects.filter(user=request.user).count()
    # ✅ DISTINCT students across ALL classes using student_uid
    total_students = Student.objects.filter(
        classroom__user=request.user
    ).values('student_uid').distinct().count()
    return JsonResponse({
        "classes": total_classes,
        "students": total_students
    })
#top 10
@login_required(login_url='login')
def dashboard_top_students(request):

    from .tasks import compute_top_students

    compute_top_students(request.user.id)

    return JsonResponse({
        "status": "processing",
        "message": "Top students are being computed in background"
    })
@login_required(login_url='login')
def get_top_students(request):

    top_students = TopStudent.objects.filter(
        user=request.user
    ).order_by('-average')

    data = []

    for item in top_students:
        data.append({
            "name": f"{item.student.first_name} {item.student.last_name}",
            "average": round(item.average, 2)
        })

    return JsonResponse(data, safe=False)
#attendance graph
def dashboard_attendance_analytics(request):

    classes = ClassRoom.objects.filter(user=request.user)

    class_summary = []
    trend_data = {}
    day_stats = {}

    for cls in classes:

        sessions = AttendanceSession.objects.filter(classroom=cls).order_by("date_time")

        trend = []

        total_score = 0
        total_sessions = 0

        for session in sessions:

            records = AttendanceRecord.objects.filter(session=session)

            if not records.exists():
                continue

            session_score = 0
            count = 0

            for r in records:
                if r.status == "Present":
                    session_score += 1
                elif r.status == "Late":
                    session_score += 0.5
                else:
                    session_score += 0

                count += 1

            if count == 0:
                continue

            pct = (session_score / count) * 100
            trend.append({
                "date": session.date_time.strftime("%Y-%m-%d"),
                "value": round(pct, 2)
            })

            total_score += pct
            total_sessions += 1

            # DAY ANALYSIS
            day = session.date_time.strftime("%A")
            day_stats.setdefault(day, []).append(pct)

        avg = round(total_score / total_sessions, 2) if total_sessions else 0

        class_summary.append({
            "name": cls.name,
            "average": avg
        })

        trend_data[cls.name] = trend

    # 🔥 compute worst day
    worst_day = None
    worst_value = 100

    for day, values in day_stats.items():
        avg = sum(values) / len(values)
        if avg < worst_value:
            worst_value = avg
            worst_day = day

    return JsonResponse({
        "classes": class_summary,
        "trend": trend_data,
        "worst_day": worst_day
    })


