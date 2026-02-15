import random
from decimal import Decimal
from faker import Faker
from django.contrib.auth import get_user_model
from store.models import Category, Product

fake = Faker()
User = get_user_model()

# Categories
if Category.objects.count() == 0:
    created = 0
    while created < 5:
        name = fake.unique.word().title()
        obj, was_created = Category.objects.get_or_create(name=name)
        if was_created:
            created += 1

# Users (optional)
if User.objects.count() == 0:
    for _ in range(10):
        User.objects.create_user(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password="password123",
        )

# Products (no images created)
if Product.objects.count() == 0:
    categories = list(Category.objects.all())

    created = 0
    while created < 20:
        name = f"{fake.unique.word().title()} {fake.unique.word().title()}"  # avoid unique collisions
        obj, was_created = Product.objects.get_or_create(
            name=name,
            defaults={
                "category": random.choice(categories),
                "description": fake.text(max_nb_chars=300),
                "price": Decimal(str(round(random.uniform(10, 100), 2))),
                "stock": random.randint(0, 50),
                "is_active": True,
            },
        )
        if was_created:
            created += 1
