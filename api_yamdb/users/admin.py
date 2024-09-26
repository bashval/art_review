from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Users


UserAdmin.fieldsets += (
    ('Дополнительные поля', {'fields': ('bio', 'role')}),
)
admin.site.register(Users, UserAdmin)
