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
