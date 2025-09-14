from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'cattle', views.CattleViewSet)
router.register(r'healthchecks', views.HealthCheckViewSet)

app_name = 'cattle'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.cattle_list, name='cattle_list'),
    path('<int:cattle_id>/', views.cattle_detail, name='cattle_detail'),
    path('<int:cattle_id>/add-healthcheck/', views.add_healthcheck, name='add_healthcheck'),
    path('select-cattle/', views.select_cattle_for_healthcheck, name='select_cattle_for_healthcheck'),
    path('edit/<int:cattle_id>/', views.cattle_edit, name='cattle_edit'),
    path('add/', views.add_cattle, name='cattle_add'),
    path('delete/<int:cattle_id>/', views.cattle_delete, name='cattle_delete'),
    

    # ปฏิทินฟาร์ม
    path('calendar/', views.farm_calendar, name='farm_calendar'),
    path('calendar/events/', views.farm_calendar_events, name='farm_calendar_events'),
    path('calendar/add-event/', views.add_calendar_event, name='add_calendar_event'),
    path('calendar/update-event/<int:event_id>/', views.update_calendar_event, name='update_calendar_event'),
    path('calendar/delete-event/<int:event_id>/', views.delete_calendar_event, name='delete_calendar_event'),
    path('api/calendar-events/', views.get_calendar_events, name='api_calendar_events'),

    path('api/', include(router.urls)),
]
