from django.contrib import admin
from .models import Sport, Match

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    ordering = ('order', 'name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'sport', 'start_time', 'league', 'status', 'is_active')
    list_filter = ('sport', 'status', 'is_active', 'start_time')
    search_fields = ('team1', 'team2', 'league')
    ordering = ('-start_time',)
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('sport', 'team1', 'team2', 'start_time', 'league', 'country')
        }),
        ('Коэффициенты', {
            'fields': ('coefficient_team1', 'coefficient_team2', 'coefficient_draw',
                      'total_over', 'total_under')
        }),
        ('Статус', {
            'fields': ('status', 'is_active', 'result', 'score')
        }),
        ('Дополнительно', {
            'fields': ('external_id', 'team1_logo', 'team2_logo'),
            'classes': ('collapse',)
        }),
    )