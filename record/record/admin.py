from django.contrib import admin
from .models import (Record, ClassRoom, Student, Activity, ActivityScore, CalendarEvent, AttendanceSession, AttendanceRecord,
TopStudent,)

admin.site.register(ClassRoom)
admin.site.register(Record)
admin.site.register(Student)
admin.site.register(Activity)
admin.site.register(ActivityScore)
admin.site.register(CalendarEvent)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
admin.site.register(TopStudent)
