from django.contrib import admin

from modules.rides.models import Ride, RideEvent


class RideEventInline(admin.TabularInline):
    model = RideEvent
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("id_ride", "status", "id_rider", "id_driver", "pickup_time")
    list_filter = ("status",)
    search_fields = ("id_rider__email", "id_driver__email")
    ordering = ("-pickup_time",)
    inlines = [RideEventInline]


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ("id_ride_event", "id_ride", "description", "created_at")
    list_filter = ("created_at",)
    search_fields = ("description",)
    ordering = ("-created_at",)
