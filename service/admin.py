from django.contrib import admin
from .models import Template, BaseTemplate

# Register your models here.
admin.site.register(Template)
admin.site.register(BaseTemplate)