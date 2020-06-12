from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from . models import Course, Lesson
from memberships.models import Client

class CourseListView(ListView):
    model= Course

class CourseDetailView(DetailView):
    model= Course

class LessonDetailView(View):
    def get(self, request, course_slug, lesson_slug, *args, **kwargs):
        course_qs= Course.objects.filter(slug=course_slug)
        if course_qs.exists():
            course=course_qs.first()

        lesson_qs= course.lessons.filter(slug=lesson_slug)
        if lesson_qs.exists():
            lesson=lesson_qs.first()

        client_membership= Client.objects.filter(user=request.user).first()
        client_membership_type= client_membership.membership

        course_allowed_mem_types=course.allowed_memberships.all()

        context = {
            'object': None
        }
        
        if course_allowed_mem_types.filter(membership_type=client_membership_type).exists():
            context={'object':lesson}

        return render(request, 'courses/lesson_detail.html', context)