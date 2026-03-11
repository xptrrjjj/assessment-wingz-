import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from modules.accounts.models import User
from modules.rides.models import Ride, RideEvent, RideStatus


class Command(BaseCommand):
    help = "Seed the database with sample users, rides, and ride events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--rides",
            type=int,
            default=50,
            help="Number of rides to create (default: 50)",
        )

    def handle(self, *args, **options):
        ride_count = options["rides"]
        self._create_users()
        self._create_rides(ride_count)
        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))

    def _create_users(self):
        users_data = [
            {"email": "admin@wingz.com", "first_name": "Admin", "last_name": "User", "role": "admin"},
            {"email": "chris.h@wingz.com", "first_name": "Chris", "last_name": "H", "role": "driver"},
            {"email": "howard.y@wingz.com", "first_name": "Howard", "last_name": "Y", "role": "driver"},
            {"email": "randy.w@wingz.com", "first_name": "Randy", "last_name": "W", "role": "driver"},
            {"email": "rider1@wingz.com", "first_name": "Alice", "last_name": "Rider", "role": "rider"},
            {"email": "rider2@wingz.com", "first_name": "Bob", "last_name": "Rider", "role": "rider"},
            {"email": "rider3@wingz.com", "first_name": "Carol", "last_name": "Rider", "role": "rider"},
        ]
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": data["role"],
                    "phone_number": f"+1555{random.randint(1000000, 9999999)}",
                    "is_staff": data["role"] == "admin",
                },
            )
            if created:
                user.set_password("password123")
                user.save(update_fields=["password"])
                self.stdout.write(f"  Created user: {user.email} ({user.role})")

    def _create_rides(self, count):
        drivers = list(User.objects.filter(role="driver"))
        riders = list(User.objects.filter(role="rider"))

        if not drivers or not riders:
            self.stderr.write("Need at least one driver and one rider.")
            return

        statuses = [RideStatus.EN_ROUTE, RideStatus.PICKUP, RideStatus.DROPOFF]
        now = timezone.now()

        rides_to_create = []
        for i in range(count):
            pickup_time = now - timedelta(days=random.randint(0, 120), hours=random.randint(0, 23))
            rides_to_create.append(
                Ride(
                    status=random.choice(statuses),
                    id_rider=random.choice(riders),
                    id_driver=random.choice(drivers),
                    pickup_latitude=round(random.uniform(25.0, 48.0), 6),
                    pickup_longitude=round(random.uniform(-122.0, -73.0), 6),
                    dropoff_latitude=round(random.uniform(25.0, 48.0), 6),
                    dropoff_longitude=round(random.uniform(-122.0, -73.0), 6),
                    pickup_time=pickup_time,
                )
            )

        Ride.objects.bulk_create(rides_to_create)
        self.stdout.write(f"  Created {count} rides.")

        rides = list(Ride.objects.all())
        events_to_create = []
        for ride in rides:
            pickup_event_time = ride.pickup_time
            events_to_create.append(
                RideEvent(
                    id_ride=ride,
                    description="Status changed to pickup",
                    created_at=pickup_event_time,
                )
            )
            if ride.status == RideStatus.DROPOFF:
                dropoff_time = pickup_event_time + timedelta(minutes=random.randint(10, 120))
                events_to_create.append(
                    RideEvent(
                        id_ride=ride,
                        description="Status changed to dropoff",
                        created_at=dropoff_time,
                    )
                )
            # Add a recent event for some rides (within last 24h) to test todays_ride_events
            if random.random() < 0.3:
                events_to_create.append(
                    RideEvent(
                        id_ride=ride,
                        description="Driver en route to pickup",
                        created_at=now - timedelta(hours=random.randint(1, 23)),
                    )
                )

        RideEvent.objects.bulk_create(events_to_create)
        self.stdout.write(f"  Created {len(events_to_create)} ride events.")
