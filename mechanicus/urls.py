from django.urls import path

from . import views

app_name = "mechanicus"

urlpatterns = [
    path("", views.index, name="index"),
    path("jobs", views.jobs, name="jobs"),
    path("jobs/forms/<str:action>", views.jobForm, name="jobForms"),
    path("skillRegister", views.skillRegister, name="skillRegister")
]
