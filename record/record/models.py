from django.db import models
from django.contrib.auth.models import User
import uuid

class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class ClassRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    year = models.CharField(max_length=50, blank=True)
    room = models.CharField(max_length=100, blank=True)
    schedule = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
class Student(models.Model):
    student_uid = models.UUIDField(default=uuid.uuid4, editable=False)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
class Activity(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    points = models.IntegerField()
    period = models.CharField(max_length=50)
    term = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
class ActivityScore(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)  # can be empty
    class Meta:
        unique_together = ('activity', 'student')
class CalendarEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} on {self.date} ({self.user.username})"
class AttendanceSession(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    period = models.CharField(max_length=20)  # prelim, midterm, etc
    date_time = models.DateTimeField()  # when attendance started
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.classroom.name} - {self.period} - {self.date_time}"
class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Late', 'Late'),
        ('Absent', 'Absent'),
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)  # when marked

    class Meta:
        unique_together = ('session', 'student')
class TopStudent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    average = models.FloatField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.average}"
