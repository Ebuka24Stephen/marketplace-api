A Django REST Framework backend for an e-commerce parts catalog with products, categories, product images, and a session-based shopping cart with payment integration gateway(e.g paystack or stripe). 

## Features
- Product & Category API (list/detail)
- Product images support (multipart upload)
- Session-based cart (works for anonymous users)
-  Add to cart, update quantity, delete cart item
-  Stock checks to prevent over-ordering
-  Django Admin for managing store data
- Redis for caching products
- Celery for Aynchronous operations


---

## Tech Stack
- Python 
- Django
- Django REST Framework
- SQLite (dev) / PostgreSQL (prod-ready)
- Redis
- Celery
