from django.contrib import admin
from django.urls import path

from emails.views import health_check, read_test_email, analyze_test_email


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("emails/test/", read_test_email),
    path("emails/analyze/",analyze_test_email
),
]