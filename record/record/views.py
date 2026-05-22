from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import json
from record.models import ClassRoom
from django.views.decorators.http import require_http_methods
from .models import ActivityScore, AttendanceRecord, AttendanceSession, Student, ClassRoom, Activity, CalendarEvent, TopStudent
import uuid
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,timedelta
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_datetime

def home(request):
    return redirect('login')

#LOGIN
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # logs user in
            return JsonResponse({
                "status": "success",
                "redirect": "/main_page/"
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid username or password"
            })

    return render(request, 'login.html')

#LOGOUT
@login_required(login_url='login')
def logout_view(request):
    logout(request)  # logs the user out
    return redirect('login')




#SIGNUP
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": "error",
                "message": "Username already exists"
            })

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "status": "error",
                "message": "Email already exists"
            })

        if password1 != password2:
            return JsonResponse({
                "status": "error",
                "message": "Passwords do not match"
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        return JsonResponse({
            "status": "success",
            "message": "Account created successfully!"
        })

    return render(request, 'signup.html')





#main page
@login_required(login_url='login')
def main_page(request):
    return render(request, 'dashboard.html')




#dashboard
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









#classroom
@login_required(login_url='login')
def classroom(request):
    classes_qs = ClassRoom.objects.filter(user=request.user)

    classes = []

    for cls in classes_qs:
        students = list(
            Student.objects.filter(classroom=cls)
            .values("id", "first_name", "last_name", "student_uid")
        )

        classes.append({
            "id": cls.id,
            "name": cls.name,
            "year": cls.year,
            "room": cls.room,
            "schedule": cls.schedule,
            "description": cls.description,
            "students": students
        })

    return render(request, 'classroom.html', {'classes': classes})
#save classroom
@login_required(login_url='login')
def save_classroom(request):
    if request.method == "POST":
        data = json.loads(request.body)

        classroom = ClassRoom.objects.create(
            user=request.user,
            name=data.get('name'),
            year=data.get('year'),
            room=data.get('room'),
            schedule=data.get('schedule'),
            description=data.get('description')
        )

        return JsonResponse({
            "id": classroom.id,
            "name": classroom.name,
            "year": classroom.year,
            "schedule": classroom.schedule,
            "room": classroom.room,
            "description": classroom.description
        })
#delete classroom
@require_http_methods(["DELETE"])
@login_required(login_url='login')
def delete_classroom(request, id):
    try:
        classroom = ClassRoom.objects.get(id=id, user=request.user)
        classroom.delete()

        return JsonResponse({
            "success": True,
            "message": "Class deleted"
        })

    except ClassRoom.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Not found"
        }, status=404)
#editing classroom
@require_http_methods(["PUT"])
@login_required(login_url='login')
def update_classroom(request, id):
    data = json.loads(request.body)

    classroom = ClassRoom.objects.get(id=id, user=request.user)

    classroom.name = data.get("name")
    classroom.year = data.get("year")
    classroom.room = data.get("room")
    classroom.schedule = data.get("schedule")
    classroom.description = data.get("description")
    classroom.save()

    return JsonResponse({
        "id": classroom.id,
        "name": classroom.name,
        "year": classroom.year,
        "room": classroom.room,
        "schedule": classroom.schedule,
        "description": classroom.description
    })
#enroll student
@login_required(login_url='login')
@require_http_methods(["POST"])
def save_student(request):
    data = json.loads(request.body)

    classroom_id = data.get("classroom_id")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    extra_class_ids = data.get("extra_class_ids", []) 

    try:
        classroom = ClassRoom.objects.get(id=classroom_id, user=request.user)
    except ClassRoom.DoesNotExist:
        return JsonResponse({"error": "Class not found"}, status=404)

    # ✅ CREATE ONE UNIQUE ID FOR THIS PERSON
    student_uid = uuid.uuid4()

    # ✅ MAIN CLASS
    student = Student.objects.create(
        classroom=classroom,
        first_name=first_name,
        last_name=last_name,
        student_uid=student_uid
    )

    # ✅ EXTRA CLASSES (same UID)
    for class_id in extra_class_ids:
        try:
            extra_class = ClassRoom.objects.get(id=class_id, user=request.user)

            Student.objects.create(
                classroom=extra_class,
                first_name=first_name,
                last_name=last_name,
                student_uid=student_uid
            )
        except ClassRoom.DoesNotExist:
            continue

    return JsonResponse({
        "id": student.id,
        "first_name": student.first_name,
        "student_uid": str(student.student_uid),
        "last_name": student.last_name
    })
#update student
@require_http_methods(["PUT"])
@login_required(login_url='login')
def update_student(request, id):
    data = json.loads(request.body)

    student = Student.objects.get(id=id, classroom__user=request.user)

    Student.objects.filter(
        student_uid=student.student_uid,
        classroom__user=request.user
    ).update(
        first_name=data.get("first_name"),
        last_name=data.get("last_name")
    )

    return JsonResponse({
        "id": student.id,
        "student_uid": str(student.student_uid),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name")
    })
#delete student
@require_http_methods(["DELETE"])
@login_required(login_url='login')
def delete_student(request, id):
    try:
        student = Student.objects.get(id=id, classroom__user=request.user)
        student.delete()

        return JsonResponse({"success": True})

    except Student.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)
#add acts
@csrf_exempt
def save_activity(request):
    if request.method == "POST":
        data = json.loads(request.body)

        classroom = ClassRoom.objects.get(id=data["classroom_id"])

        activity = Activity.objects.create(
            classroom=classroom,
            name=data["name"],
            type=data["type"],
            points=data["points"],
            period=data["period"],
            term=data["term"]
        )

        return JsonResponse({
            "id": activity.id,
            "name": activity.name,
            "type": activity.type,
            "points": activity.points,
            "period": activity.period,
            "term": activity.term
        })
def get_activities(request, class_id, term):
    activities = Activity.objects.filter(
        classroom_id=class_id,
        term=term
    ).values("id", "name", "type", "points", "period")

    return JsonResponse(list(activities), safe=False)
#del acts
@csrf_exempt
def delete_activity(request, activity_id):
    if request.method == "POST":
        try:
            activity = Activity.objects.get(id=activity_id)
            activity.delete()
            return JsonResponse({"success": True})
        except Activity.DoesNotExist:
            return JsonResponse({"success": False})
#populate acts student table
@login_required(login_url='login')
def get_activity_students(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id, classroom__user=request.user)

        students = Student.objects.filter(classroom=activity.classroom)

        result = []

        for student in students:
            score_obj = ActivityScore.objects.filter(
                activity=activity,
                student=student
            ).first()

            result.append({
                "student_id": student.id,
                "name": f"{student.first_name} {student.last_name}",
                "score": score_obj.score if score_obj else None
            })

        return JsonResponse(result, safe=False)

    except Activity.DoesNotExist:
        return JsonResponse([], safe=False)
@csrf_exempt
@login_required(login_url='login')
def save_activity_scores(request, activity_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            activity = Activity.objects.get(
                id=activity_id,
                classroom__user=request.user
            )

            # update activity details
            activity.name = data.get("name", activity.name)
            activity.type = data.get("type", activity.type)
            activity.points = data.get("points", activity.points)
            activity.save()
            # EXISTING LOOP
            for item in data["scores"]:
                student_id = item.get("student_id")
                score = item.get("score")

                if not student_id:
                    continue

                try:
                    student = Student.objects.get(id=student_id)
                except Student.DoesNotExist:
                    continue

                ActivityScore.objects.update_or_create(
                    activity=activity,
                    student=student,
                    defaults={"score": score}
                )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400) 
@login_required(login_url='login')
def get_student_activities(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        activities = Activity.objects.filter(classroom=student.classroom)
        result = []
        for act in activities:
            score_obj = ActivityScore.objects.filter(
                activity=act,
                student=student
            ).first()

            result.append({
                "id": act.id,
                "name": act.name,
                "type": act.type,
                "points": act.points,
                "term": act.term,
                "score": score_obj.score if score_obj else None
            })

        return JsonResponse(result, safe=False)

    except Student.DoesNotExist:
        return JsonResponse([], safe=False)
#attendance percentage
def get_student_attendance(request, student_id, classroom_id):
    sessions = AttendanceSession.objects.filter(classroom_id=classroom_id)

    total_sessions = sessions.count()

    if total_sessions == 0:
        return JsonResponse({"attendance": 0})

    records = AttendanceRecord.objects.filter(
        session__classroom_id=classroom_id,
        student_id=student_id
    )

    score = 0

    for session in sessions:
        record = records.filter(session=session).first()

        if not record or not record.status:
            score += 0  # absent
        elif record.status == "Present":
            score += 1
        elif record.status == "Late":
            score += 0.5
        elif record.status == "Absent":
            score += 0

    percentage = (score / total_sessions) * 100

    return JsonResponse({
        "attendance": round(percentage, 2)
    })
#acts score grades
def get_student_grades(request, student_id, classroom_id):

    periods = ["prelim", "midterm", "prefinal", "final"]

    result = {}
    period_numeric = {}
    has_inc = False  # track if ANY period is INC

    for period in periods:

        activities = Activity.objects.filter(
            classroom_id=classroom_id,
            term=period
        )

        quiz_total = quiz_score = 0
        exam_total = exam_score = 0
        rec_total = rec_score = 0

        period_has_null = False  # track INC per period

        for act in activities:
            score_obj = ActivityScore.objects.filter(
                activity=act,
                student_id=student_id
            ).first()

            # 🚨 CHECK NULL → INC
            if not score_obj or score_obj.score is None:
                period_has_null = True
                continue

            score = score_obj.score

            if act.type in ["Quiz", "Activity"]:
                quiz_total += act.points
                quiz_score += score

            elif act.type == "Exam":
                exam_total += act.points
                exam_score += score

            elif act.type == "Recitation":
                rec_total += act.points
                rec_score += score

        # 🚨 IF ANY NULL → INC
        if period_has_null:
            result[period] = "INC"
            has_inc = True
            continue

        # compute normally
        quiz_pct = (quiz_score / quiz_total * 100) if quiz_total else 0
        exam_pct = (exam_score / exam_total * 100) if exam_total else 0
        rec_pct = (rec_score / rec_total * 100) if rec_total else 0

        grade = (
            quiz_pct * 0.30 +
            exam_pct * 0.50 +
            rec_pct * 0.20
        )

        result[period] = round(grade, 2)
        period_numeric[period] = grade

    # 🚨 IF ANY PERIOD INC → FINAL INC
    if has_inc:
        return JsonResponse({
            "periods": result,
            "final_average": "INC",
            "final_grade": "INC"
        })

    # compute final average
    final_avg = sum(period_numeric.values()) / 4

    def convert_to_scale(avg):
        if avg >= 95: return 1.00
        elif avg >= 90: return 1.50
        elif avg >= 85: return 2.00
        elif avg >= 80: return 2.50
        elif avg >= 75: return 3.00
        else: return 5.00

    final_grade = convert_to_scale(final_avg)

    return JsonResponse({
        "periods": result,
        "final_average": round(final_avg, 2),
        "final_grade": final_grade
    })
#class attendance graph
def get_class_attendance_summary(request, classroom_id):

    sessions = AttendanceSession.objects.filter(classroom_id=classroom_id)

    total = sessions.count()

    if total == 0:
        return JsonResponse({
            "present": 0,
            "late": 0,
            "absent": 0
        })

    present = late = absent = 0

    records = AttendanceRecord.objects.filter(session__classroom_id=classroom_id)

    for r in records:
        if not r.status:
            absent += 1
        elif r.status == "Present":
            present += 1
        elif r.status == "Late":
            late += 1
        elif r.status == "Absent":
            absent += 1

    def pct(x):
        return round((x / (present + late + absent)) * 100, 2) if (present + late + absent) else 0

    return JsonResponse({
        "present": pct(present),
        "late": pct(late),
        "absent": pct(absent)
    })
#total students
def class_student_count(request, class_id):
    count = Student.objects.filter(classroom_id=class_id).count()
    return JsonResponse({"total": count})






#attendance
@login_required(login_url='login')
def attendance(request):
    classrooms = ClassRoom.objects.filter(user=request.user)

    return render(request, 'attendance.html', {
        'classrooms': classrooms
    })
@login_required(login_url='login')
def get_students(request, class_id):
    try:
        classroom = ClassRoom.objects.get(id=class_id, user=request.user)
    except ClassRoom.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)

    students = Student.objects.filter(classroom=classroom)

    data = []
    for s in students:
        data.append({
            'id': str(s.student_uid),
            'name': f"{s.first_name} {s.last_name}"
        })

    return JsonResponse({'students': data})
#get attendance
@csrf_exempt
@login_required(login_url='login')
def save_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)

        class_id = data.get("classId")
        period = data.get("period")
        date_time = parse_datetime(data.get("date_time"))
        records = data.get("records")

        classroom = ClassRoom.objects.get(id=class_id, user=request.user)

        session = AttendanceSession.objects.create(
            classroom=classroom,
            period=period,
            date_time=date_time
        )

        for r in records:
            student = Student.objects.get( student_uid=r["studentId"],classroom=classroom)

            status = r.get("status") or None
            timestamp = parse_datetime(r["timestamp"]) if r.get("timestamp") else None

            AttendanceRecord.objects.create(
                session=session,
                student=student,
                status=status,
                timestamp=timestamp
            )

        return JsonResponse({"message": "Saved successfully"})
@login_required(login_url='login')
def get_attendance(request, class_id, period):
    classroom = ClassRoom.objects.get(id=class_id, user=request.user)

    sessions = AttendanceSession.objects.filter(
        classroom=classroom,
        period=period
    ).order_by('-date_time')

    session_list = []
    for s in sessions:
        session_list.append({
            "id": s.id,
            "date_time": s.date_time,
        })

    latest = sessions.first()

    records = []

    if latest:
        students = Student.objects.filter(classroom=classroom)

        for student in students:
            record, created = AttendanceRecord.objects.get_or_create(
                session=latest,
                student=student,
                defaults={
                    "status": None,
                    "timestamp": None
                }
            )

            records.append({
                "studentId": str(student.student_uid),
                "status": record.status,
                "timestamp": record.timestamp
            })

    return JsonResponse({
        "sessions": session_list,
        "latest": {
            "id": latest.id if latest else None,
            "date_time": latest.date_time if latest else None,
            "records": records
        }
    })
@login_required(login_url='login')
def get_session(request, session_id):
    session = AttendanceSession.objects.get(
        id=session_id,
        classroom__user=request.user
    )

    records = []
    for r in session.records.all():
        records.append({
            "studentId": str(r.student.student_uid),
            "status": r.status,
            "timestamp": r.timestamp
        })

    return JsonResponse({
        "date_time": session.date_time,
        "records": records
    })
#del attendance
@login_required(login_url='login')
def delete_session(request, session_id):
    session = AttendanceSession.objects.get(
        id=session_id,
        classroom__user=request.user
    )
    session.delete()

    return JsonResponse({"message": "deleted"})
#update attendance
@csrf_exempt
@login_required(login_url='login')
def update_attendance(request, session_id):
    if request.method == "POST":
        data = json.loads(request.body)
        student_id = data.get("studentId")
        new_status = data.get("status")

        try:
            session = AttendanceSession.objects.get(
                id=session_id,
                classroom__user=request.user
            )
        except AttendanceSession.DoesNotExist:
            return JsonResponse({"error": "Session not found"}, status=404)

        try:
            record = AttendanceRecord.objects.get(
                session=session,
                student__student_uid=student_id
            )
        except AttendanceRecord.DoesNotExist:
            return JsonResponse({"error": "Record not found"}, status=404)

        now = timezone.now()

        # 🔥 recompute status based on original session time
        diff_minutes = (now - session.date_time).total_seconds() / 60

        if new_status == "Present":
            new_status = "Present" if diff_minutes <= 30 else "Late"

        record.status = new_status
        record.timestamp = now
        record.save()

        return JsonResponse({
            "message": "updated",
            "status": record.status,
            "timestamp": record.timestamp
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
