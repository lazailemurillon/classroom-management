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

#schedule
@login_required(login_url='login')
def schedule(request):
    return render(request, 'schedule.html')
# Get events
@login_required
def get_events(request):
    events = CalendarEvent.objects.filter(user=request.user)
    data = {}
    for event in events:
        date_str = event.date.strftime("%Y-%m-%d")
        if date_str not in data:
            data[date_str] = []
        data[date_str].append({"id": event.id, "title": event.title})
    return JsonResponse(data)

# Add event
@login_required
@csrf_exempt
def add_event(request):
    if request.method == "POST":
        body = json.loads(request.body)
        title = body.get("title")
        date_str = body.get("date")
        if not title or not date_str:
            return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        event = CalendarEvent.objects.create(user=request.user, title=title, date=date_obj)
        return JsonResponse({"status": "success", "id": event.id})
# Delete event
@login_required
@csrf_exempt
def delete_event(request):
    if request.method == "POST":
        body = json.loads(request.body)
        event_id = body.get("id")
        try:
            event = CalendarEvent.objects.get(id=event_id, user=request.user)
            event.delete()
            return JsonResponse({"status": "success"})
        except CalendarEvent.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Event not found"}, status=404)
#upcoming event
@login_required(login_url='login')
def upcoming_events(request):
    today = timezone.now().date()
    end_date = today + timedelta(days=14)

    events = CalendarEvent.objects.filter(
        user=request.user,
        date__range=[today, end_date]
    ).order_by('date')

    data = [
        {
            "title": e.title,
            "date": e.date.strftime("%b %d, %Y"),
        }
        for e in events
    ]

    return JsonResponse({"events": data})
