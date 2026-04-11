from django.contrib import admin
from .models import AutoApplyPermission, ApplicationQueue, AuditLog


@admin.register(AutoApplyPermission)
class AutoApplyPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'allowed', 'daily_limit', 'require_approval', 'terms_accepted', 'granted_at')
    list_filter = ('allowed', 'require_approval')
    search_fields = ('user__username', 'user__email')


@admin.register(ApplicationQueue)
class ApplicationQueueAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'match_score', 'status', 'queued_at', 'applied_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'job__title')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'status', 'job', 'timestamp')
    list_filter = ('status', 'action')
    search_fields = ('user__username', 'action')
    readonly_fields = ('user', 'job', 'action', 'status', 'detail', 'timestamp')
