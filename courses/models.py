from django.db import models
from memberships.models import Membership
from django.urls import reverse


class Course(models.Model):
    title = models.CharField(max_length=200)
    description= models.TextField()
    allowed_memberships= models.ManyToManyField(Membership)
    slug= models.SlugField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug':self.slug})
    
    @property
    def lessons(self):
        return self.lesson_set.all().order_by('position')

class Lesson(models.Model):
    title= models.CharField(max_length= 50)
    course=models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    position= models.IntegerField()
    video_url=models.CharField(max_length=180)
    slug= models.SlugField()
    thumbnail= models.ImageField()

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse('courses:lesson-detail', kwargs={'course_slug':self.course.slug, 
                                                            'lesson_slug':self.slug})