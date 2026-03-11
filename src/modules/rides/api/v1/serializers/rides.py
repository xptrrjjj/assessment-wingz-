from rest_framework import serializers


class UserBriefSerializer(serializers.Serializer):
    id_user = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class RideEventSerializer(serializers.Serializer):
    id_ride_event = serializers.IntegerField(read_only=True)
    description = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class RideListSerializer(serializers.Serializer):
    id_ride = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    id_rider = UserBriefSerializer(read_only=True)
    id_driver = UserBriefSerializer(read_only=True)
    pickup_latitude = serializers.FloatField(read_only=True)
    pickup_longitude = serializers.FloatField(read_only=True)
    dropoff_latitude = serializers.FloatField(read_only=True)
    dropoff_longitude = serializers.FloatField(read_only=True)
    pickup_time = serializers.DateTimeField(read_only=True)
    todays_ride_events = RideEventSerializer(many=True, read_only=True)
    distance = serializers.FloatField(read_only=True, required=False, default=None)
