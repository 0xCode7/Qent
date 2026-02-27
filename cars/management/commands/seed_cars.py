import os
import random
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import connection, transaction

from cars.models import Brand, Color, CarFeature, Car, CarImage, Review
from authentication.models import User, Location


class Command(BaseCommand):
    help = "Seed database with brands, cars, features, colors, and locations"

    # -----------------------------
    # Clear Data Safely
    # -----------------------------
    def clear_data(self):
        CarImage.objects.all().delete()
        Review.objects.all().delete()

        # Safe M2M clear
        Car.car_features.through.objects.all().delete()

        Car.objects.all().delete()
        Brand.objects.all().delete()
        Color.objects.all().delete()
        CarFeature.objects.all().delete()

    # -----------------------------
    # Reset Postgres Sequences
    # -----------------------------
    def reset_sequences(self):
        with connection.cursor() as cursor:
            tables = [
                "cars_car",
                "cars_carimage",
                "cars_brand",
                "cars_color",
                "cars_carfeature",
                "cars_review",
                "authentication_user",
                "authentication_location",
            ]

            for table in tables:
                cursor.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), 1, false);"
                )

    # -----------------------------
    # Handle
    # -----------------------------
    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Clearing old data...")
        self.clear_data()
        self.reset_sequences()

        # -----------------------------
        # Paths
        # -----------------------------
        default_brands_path = os.path.join(settings.MEDIA_ROOT, "default/brands")
        default_cars_path = os.path.join(settings.MEDIA_ROOT, "default/cars")

        os.makedirs(os.path.join(settings.MEDIA_ROOT, "brands"), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "cars"), exist_ok=True)

        # -----------------------------
        # Colors
        # -----------------------------
        colors = [
            Color.objects.create(name="Red", hex_value="#FF0000"),
            Color.objects.create(name="Blue", hex_value="#0000FF"),
            Color.objects.create(name="Black", hex_value="#000000"),
            Color.objects.create(name="White", hex_value="#FFFFFF"),
            Color.objects.create(name="Silver", hex_value="#C0C0C0"),
        ]

        # -----------------------------
        # Fuel Types (Reusable)
        # -----------------------------
        fuel_types = [
            CarFeature.objects.create(
                name="Fuel Type", value="Petrol", image="icons/fuel.svg"
            ),
            CarFeature.objects.create(
                name="Fuel Type", value="Diesel", image="icons/fuel.svg"
            ),
            CarFeature.objects.create(
                name="Fuel Type", value="Electric", image="icons/fuel.svg"
            ),
            CarFeature.objects.create(
                name="Fuel Type", value="Hybrid", image="icons/fuel.svg"
            ),
        ]

        # -----------------------------
        # Locations
        # -----------------------------
        location_list = [
            ("Cairo", "Nasr City", 30.0626, 31.2808),
            ("Cairo", "Maadi", 29.9714, 31.2764),
            ("Cairo", "Heliopolis", 30.0820, 31.3122),
            ("Giza", "Dokki", 30.0241, 31.2103),
            ("Giza", "Mohandessin", 30.0617, 31.2161),
            ("Alexandria", "Stanley", 31.2211, 29.9150),
        ]

        locations = []
        for gov, region, lat, lng in location_list:
            loc, _ = Location.objects.get_or_create(
                name=f"{region}, {gov}",
                defaults={"lat": lat, "lng": lng},
            )
            locations.append(loc)

        # -----------------------------
        # Brand Models
        # -----------------------------
        brand_models = {
            "BMW": ["X5", "X6", "M3", "M4", "i8"],
            "Ferrari": ["488 GTB", "Portofino", "F8 Tributo", "Roma", "SF90"],
            "Lamborghini": ["Huracan", "Aventador", "Urus", "Sian"],
            "Tesla": ["Model S", "Model 3", "Model X", "Model Y"],
        }

        # -----------------------------
        # Brands & Cars
        # -----------------------------
        for brand_file in os.listdir(default_brands_path):
            brand_name, _ = os.path.splitext(brand_file)

            brand = Brand.objects.create(name=brand_name)

            with open(os.path.join(default_brands_path, brand_file), "rb") as f:
                brand.image.save(brand_file, File(f), save=True)

            car_files = [
                f
                for f in os.listdir(default_cars_path)
                if brand_name.lower() in f.lower()
            ]

            if not car_files:
                continue

            models = brand_models.get(brand_name, ["Generic"])

            for _ in range(random.randint(5, 8)):
                model_name = random.choice(models)
                car_file = random.choice(car_files)

                is_for_rent = random.choice([True, False])
                is_for_pay = random.choice([True, False])

                car = Car.objects.create(
                    name=f"{brand_name} {model_name}",
                    description=f"{brand_name} {model_name} available for rent or purchase.",
                    car_type=random.choice(["Regular", "Luxury"]),
                    brand=brand,
                    color=random.choice(colors),
                    location=random.choice(locations),
                    average_rate=random.randint(3, 5),
                    available_to_book=random.choice([True, False]),
                    is_for_rent=is_for_rent,
                    daily_rent=round(random.uniform(30, 100), 2) if is_for_rent else None,
                    weekly_rent=round(random.uniform(200, 500), 2) if is_for_rent else None,
                    monthly_rent=round(random.uniform(800, 2000), 2) if is_for_rent else None,
                    yearly_rent=round(random.uniform(5000, 15000), 2) if is_for_rent else None,
                    is_for_pay=is_for_pay,
                    price=round(random.uniform(10000, 50000), 2) if is_for_pay else None,
                )

                # Main Image
                with open(os.path.join(default_cars_path, car_file), "rb") as f:
                    CarImage.objects.create(car=car, image=File(f, name=car_file))

                # Extra Images
                for i in range(2):
                    with open(os.path.join(default_cars_path, car_file), "rb") as f:
                        CarImage.objects.create(
                            car=car,
                            image=File(f, name=f"extra_{i}_{car_file}"),
                        )

                # -----------------------------
                # Dynamic Features Per Car
                # -----------------------------
                car_features = []

                car_features.append(
                    CarFeature.objects.create(
                        name="Capacity",
                        value=f"{random.randint(2,7)} Seats",
                        image="icons/seats.svg",
                    )
                )

                car_features.append(
                    CarFeature.objects.create(
                        name="Engine Output",
                        value=f"{random.randint(200,800)} HP",
                        image="icons/fuel.svg",
                    )
                )

                car_features.append(
                    CarFeature.objects.create(
                        name="Max Speed",
                        value=f"{random.randint(180,350)} km/h",
                        image="icons/speed.svg",
                    )
                )

                if random.choice([True, False]):
                    car_features.append(
                        CarFeature.objects.create(
                            name="Driving Assist",
                            value="Autopilot",
                            image="icons/autopilot.svg",
                        )
                    )

                if random.choice([True, False]):
                    car_features.append(
                        CarFeature.objects.create(
                            name="Parking Assist",
                            value="Auto Parking",
                            image="icons/parking.svg",
                        )
                    )

                selected_fuel = random.choice(fuel_types)
                car_features.append(selected_fuel)

                # Single Charge feature only for Electric / Hybrid
                if selected_fuel.value in ["Electric", "Hybrid"]:
                    car_features.append(
                        CarFeature.objects.create(
                            name="Single Charge",
                            value=f"{random.randint(250, 500)} Miles",
                            image="icons/charge.svg",
                        )
                    )

                car.car_features.set(car_features)

        # -----------------------------
        # Users & Reviews
        # -----------------------------
        if not User.objects.exists():
            for i in range(5):
                User.objects.create_user(
                    username=f"user{i+1}",
                    email=f"user{i+1}@mail.com",
                    password="password123",
                )

        users = list(User.objects.all())

        for car in Car.objects.all():
            review_users = random.sample(
                users, k=random.randint(1, min(3, len(users)))
            )

            for user in review_users:
                Review.objects.create(
                    user=user,
                    car=car,
                    review=random.choice(
                        [
                            "Great experience!",
                            "Very clean and comfortable.",
                            "Would rent again.",
                            "Smooth ride and reliable.",
                        ]
                    ),
                    rate=random.randint(3, 5),
                )

        self.stdout.write(self.style.SUCCESS("✅ Database Seeded Successfully!"))