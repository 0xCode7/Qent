import os
import random
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import connection

from cars.models import Brand, Color, CarFeature, Car, CarImage, Review
from authentication.models import User, Location


class Command(BaseCommand):
    help = "Seed database with brands, cars, features, colors, and locations"

    def clear_data(self):
        """Delete data in the right order to avoid FK constraint errors"""
        # children first
        CarImage.objects.all().delete()
        Review.objects.all().delete()
        # clear ManyToMany table directly
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM cars_car_car_features;")

        # now parents
        Car.objects.all().delete()
        Brand.objects.all().delete()
        Color.objects.all().delete()
        CarFeature.objects.all().delete()
        Location.objects.all().delete()
        User.objects.all().delete()

    def reset_sequences(self):
        """Reset sequences (Postgres version)"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT setval(pg_get_serial_sequence('cars_car', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('cars_carimage', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('cars_brand', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('cars_color', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('cars_carfeature', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('cars_review', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('authentication_user', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('authentication_location', 'id'), 1, false);")

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Clearing old data...")
        self.clear_data()
        self.reset_sequences()

        # --- Paths ---
        default_brands_path = os.path.join(settings.MEDIA_ROOT, "default/brands")
        default_cars_path = os.path.join(settings.MEDIA_ROOT, "default/cars")
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "brands"), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "cars"), exist_ok=True)

        # --- Colors ---
        colors_data = [
            ("Red", "#FF0000"),
            ("Blue", "#0000FF"),
            ("Black", "#000000"),
            ("White", "#FFFFFF"),
            ("Silver", "#C0C0C0"),
        ]
        colors = [
            Color.objects.create(name=c[0], hex_value=c[1]) for c in colors_data
        ]

        # --- Car Features ---
        features_data = [
            ("Seats",  f"{random.randint(2, 5)} Seats", "icons/seats.png"),
            ("Transmission", "Automatic", "icons/gear.png"),
            ("Air Conditioning", "Available", "icons/ac.png"),
            ("GPS", "Available", "icons/gps.png"),
            ("Bluetooth", "Available", "icons/bluetooth.png"),
        ]
        features = [
            CarFeature.objects.create(name=f[0], value=f[1], image=f[2])
            for f in features_data
        ]

        # --- Fuel Types ---
        fuel_types = [
            CarFeature.objects.create(
                name="Fuel Type", value="Petrol", image="icons/fuel.png"
            ),
            CarFeature.objects.create(
                name="Fuel Type", value="Diesel", image="icons/fuel.png"
            ),
            CarFeature.objects.create(
                name="Fuel Type", value="Electric", image="icons/fuel.png"
            ),
            CarFeature.objects.create(
                name="Fuel Type", value="Hybrid", image="icons/fuel.png"
            ),
        ]

        # --- Locations ---
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
                name=f"{region}, {gov}", defaults={"lat": lat, "lng": lng}
            )
            locations.append(loc)

        # --- Real Car Models for each Brand ---
        brand_models = {
            "BMW": ["X5", "X6", "M3", "M4", "i8"],
            "Ferrari": ["488 GTB", "Portofino", "F8 Tributo", "Roma", "SF90 Stradale"],
            "Lamborghini": ["Huracan", "Aventador", "Urus", "Sian", "Gallardo"],
            "Tesla": ["Model S", "Model 3", "Model X", "Model Y", "Roadster"],
        }

        # --- Brands & Cars ---
        for brand_file in os.listdir(default_brands_path):
            brand_name, ext = os.path.splitext(brand_file)
            brand = Brand.objects.create(name=brand_name)

            # Brand image
            with open(os.path.join(default_brands_path, brand_file), "rb") as f:
                brand.image.save(brand_file, File(f), save=True)

            # Car images for this brand
            car_files = [
                f
                for f in os.listdir(default_cars_path)
                if brand_name.lower() in f.lower()
            ]
            if not car_files:
                self.stdout.write(
                    f"⚠️ No car images found for brand {brand_name}, skipping cars."
                )
                continue

            models = brand_models.get(brand_name, ["Generic Model"])
            for _ in range(random.randint(5, 8)):  # fewer cars for speed
                model_name = random.choice(models)
                car_file = random.choice(car_files)

                is_for_rent = random.choice([True, False])
                is_for_pay = random.choice([True, False])
                car_type = random.choice(["Regular", "Luxury"])

                car = Car.objects.create(
                    name=f"{brand_name} {model_name}",
                    description=f"A stylish {brand_name} {model_name} available for rent or purchase.",
                    car_type=car_type,
                    brand=brand,
                    color=random.choice(colors),
                    location=random.choice(locations),
                    average_rate=random.randint(3, 5),
                    available_to_book=random.choice([True, False]),
                    is_for_rent=is_for_rent,
                    daily_rent=random.uniform(30, 100) if is_for_rent else None,
                    weekly_rent=random.uniform(200, 500) if is_for_rent else None,
                    monthly_rent=random.uniform(800, 2000) if is_for_rent else None,
                    yearly_rent=random.uniform(5000, 15000) if is_for_rent else None,
                    is_for_pay=is_for_pay,
                    price=random.uniform(10000, 50000) if is_for_pay else None,
                )

                # Attach main image (via CarImage)
                with open(os.path.join(default_cars_path, car_file), "rb") as f:
                    CarImage.objects.create(car=car, image=File(f, name=car_file))

                # Attach multiple extra images
                for i in range(2):  # 2 extra images per car
                    with open(os.path.join(default_cars_path, car_file), "rb") as f:
                        CarImage.objects.create(
                            car=car, image=File(f, name=f"extra_{i}_{car_file}")
                        )

                # Assign features
                car_features = random.sample(features, random.randint(2, 4))
                car_features.append(random.choice(fuel_types))
                car.car_features.set(car_features)

        # --- Users & Reviews ---
        if not User.objects.exists():
            for i in range(5):
                User.objects.create_user(
                    username=f"user{i + 1}",
                    email=f"user{i + 1}@mail.com",
                    password="password123",
                )

        users = list(User.objects.all())
        for car in Car.objects.all():
            for _ in range(random.randint(1, 3)):
                Review.objects.create(
                    user=random.choice(users),
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

        self.stdout.write(self.style.SUCCESS("✅ Database cleared and sequences reset."))
