A Django REST Framework backend for an e-commerce marketplace with products, categories, product images, session-based shopping cart, orders, and payment gateway integration (Paystack).

## Features
- Product & Category API (list/detail)
- Product images support (multipart upload)
- Session-based cart (works for anonymous users)
- Add to cart, update quantity, delete cart item
- Stock checks to prevent over-ordering
- Stock decremented on order placement, incremented on refund
- Django Admin for managing store data
- Redis for caching products
- Celery for asynchronous operations
- Paystack payment integration

---

## Tech Stack
- Python
- Django
- Django REST Framework
- SQLite (dev) / PostgreSQL (prod-ready)
- Redis
- Celery

---

## Project URLs
- **Project url**: `https://roadmap.sh/projects/ecommerce-api`
- **Local Development**: `http://localhost:8000`
- **Admin Panel**: `http://localhost:8000/admin`
- **API Base**: `http://localhost:8000/api`
- **Repository**: [GitHub - Marketplace API](https://github.com/Ebuka24Stephen/marketplace_api)
- **Live Demo**: (Coming soon)

---

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication
- **User Registration/Login**: JWT tokens (access + refresh tokens)
- **Cart**: Session-based (no authentication required)
- **Orders & Payments**: JWT authentication required

---

## API Endpoints

### 1. **User Authentication** (`/api/users/`)

#### Register User
- **Endpoint**: `POST /api/users/register/`
- **Permission**: Public (AllowAny)
- **Description**: Create a new user account
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user_serializer": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
  ```

#### Login User
- **Endpoint**: `POST /api/users/login/`
- **Permission**: Public (AllowAny)
- **Description**: Authenticate user and get JWT tokens
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
  ```

---

### 2. **Store - Products & Categories** (`/api/`)

#### List All Categories
- **Endpoint**: `GET /api/categories/`
- **Permission**: Public (AllowAny)
- **Description**: Get all product categories (cached for 1 hour)
- **Response** (200 OK):
  ```json
  [
    {
      "id": 1,
      "name": "Engine Parts",
      "slug": "engine-parts"
    }
  ]
  ```

#### List Products by Category
- **Endpoint**: `GET /api/categories/<cat_slug>/products/`
- **Permission**: Public (AllowAny)
- **Description**: Get all active products in a specific category (cached for 1 hour)
- **URL Parameters**:
  - `cat_slug`: Category slug (e.g., "engine-parts")
- **Response** (200 OK):
  ```json
  [
    {
      "id": 1,
      "name": "Piston",
      "slug": "piston",
      "category": {
        "id": 1,
        "name": "Engine Parts",
        "slug": "engine-parts"
      },
      "price": "2500.00",
      "stock": 50,
      "description": "High quality piston",
      "images": [...],
      "is_active": true,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
  ```

#### Get Product Detail
- **Endpoint**: `GET /api/categories/<cat_slug>/products/<product_slug>/`
- **Permission**: Public (AllowAny)
- **Description**: Get detailed information about a specific product (cached for 1 hour)
- **URL Parameters**:
  - `cat_slug`: Category slug
  - `product_slug`: Product slug
- **Response** (200 OK): Single product object with full details

#### List All Products
- **Endpoint**: `GET /api/products/`
- **Permission**: Public (AllowAny)
- **Description**: Get all active products across all categories (cached for 1 hour)
- **Response** (200 OK): Array of products with category information

---

### 3. **Shopping Cart** (`/api/cart/`)

#### Add Product to Cart
- **Endpoint**: `POST /api/cart/add/`
- **Permission**: Public (Session-based)
- **Description**: Add a product to cart or increment quantity if already in cart. Includes stock validation.
- **Request Body**:
  ```json
  {
    "product_id": 101,
    "quantity": 1
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "message": "Added to cart"
  }
  ```
- **Error Response** (400 Bad Request):
  ```json
  {
    "error": "Insufficient stock"
  }
  ```
- **Features**:
  - Automatically creates a cart if it doesn't exist
  - Stores cart ID in session
  - Prevents adding more items than available stock

#### Get Cart Items
- **Endpoint**: `GET /api/cart/`
- **Permission**: Public (Session-based)
- **Description**: Retrieve all items in the current cart
- **Response** (200 OK):
  ```json
  [
    {
      "cart": {
        "id": 1,
        "created_at": "..."
      },
      "product": {
        "id": 101,
        "name": "Piston",
        "price": "2500.00"
      },
      "quantity": 3
    }
  ]
  ```
- **Empty Cart Response** (200 OK):
  ```json
  {
    "message": "Cart is empty"
  }
  ```

#### Reduce Cart Item Quantity
- **Endpoint**: `POST /api/cart/<int:product_id>/quantity/`
- **Permission**: Public (Session-based)
- **Description**: Reduce quantity of a cart item by 1. Removes item if quantity reaches 0.
- **URL Parameters**:
  - `product_id`: Product ID
- **Response** (200 OK):
  ```json
  {
    "message": "Quantity reduced",
    "quantity": 2
  }
  ```
- **Response** (200 OK, if removed):
  ```json
  {
    "message": "Item removed from cart"
  }
  ```

#### Delete Cart Item
- **Endpoint**: `DELETE /api/cart/<int:product_id>/delete/`
- **Permission**: Public (Session-based)
- **Description**: Remove a specific product from the cart
- **URL Parameters**:
  - `product_id`: Product ID
- **Response** (200 OK):
  ```json
  {
    "message": "Product removed from cart"
  }
  ```

---

### 4. **Orders** (`/api/order/`)

#### Create Order
- **Endpoint**: `POST /api/order/checkout/`
- **Permission**: Authenticated (JWT required)
- **Description**: Create an order from current cart. Decrements product stock and clears cart.
- **Request Body**:
  ```json
  {
    "full_name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main St",
    "city": "Lagos",
    "phone_number": "+2348012345678"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main St",
    "city": "Lagos",
    "phone_number": "+2348012345678",
    "items": [
      {
        "id": 1,
        "product": {...},
        "price": "2500.00",
        "quantity": 3
      }
    ],
    "created": "2025-01-15T10:30:00Z",
    "updated": "2025-01-15T10:30:00Z"
  }
  ```
- **Features**:
  - Atomic transaction - decrements stock and clears cart
  - Validates cart exists and has items
  - Checks product stock availability
  - Clears cart session after order creation

#### List User Orders
- **Endpoint**: `GET /api/order/`
- **Permission**: Authenticated (JWT required)
- **Description**: Get all orders for the authenticated user
- **Response** (200 OK):
  ```json
  [
    {
      "id": 1,
      "full_name": "John Doe",
      "email": "john@example.com",
      "address": "123 Main St",
      "city": "Lagos",
      "items": [...],
      "created": "2025-01-15T10:30:00Z",
      "updated": "2025-01-15T10:30:00Z"
    }
  ]
  ```

#### Get Order Detail
- **Endpoint**: `GET /api/order/<int:pk>/`
- **Permission**: Authenticated (JWT required)
- **Description**: Get detailed information about a specific order
- **URL Parameters**:
  - `pk`: Order ID
- **Response** (200 OK): Single order object with all details

---

### 5. **Payments** (`/api/payment/`)

#### Initialize Payment
- **Endpoint**: `POST /api/payment/create/<order_id>/`
- **Permission**: Authenticated (JWT required)
- **Description**: Initialize a payment using Paystack API. Generates payment reference and authorization URL.
- **URL Parameters**:
  - `order_id`: Order ID to pay for
- **Response** (200 OK):
  ```json
  {
    "reference": "ORD_1_a1b2c3d4e5",
    "access_code": "1234567890",
    "authorization_url": "https://checkout.paystack.com/1234567890"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: "Order is already paid."
  - 400 Bad Request: "Payment already initialized."
  - 500 Internal Server Error: Payment gateway error
- **Features**:
  - Converts amount to kobo (Paystack format)
  - Creates payment record with unique reference
  - Stores Paystack access code for client
  - Includes order and user metadata

#### Verify Payment
- **Endpoint**: `GET /api/payment/verify/?reference=<reference>`
- **Permission**: Authenticated (JWT required)
- **Description**: Verify payment status with Paystack and update order if successful
- **Query Parameters**:
  - `reference`: Payment reference (returned from initialization)
- **Response** (200 OK):
  ```json
  {
    "detail": "Payment verified and order marked as paid."
  }
  ```
- **Error Response** (400 Bad Request):
  ```json
  {
    "detail": "Payment verification failed.",
    "paystack": {...}
  }
  ```
- **Features**:
  - Atomic transaction
  - Verifies with Paystack using secret key
  - Updates payment status to "paid"
  - Marks order as paid
  - Stores Paystack response metadata

---

## Request/Response Examples

### Complete Order Flow Example

#### 1. Register/Login
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "buyer@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### 2. Browse Categories
```bash
curl -X GET http://localhost:8000/api/categories/
```

#### 3. View Products in Category
```bash
curl -X GET http://localhost:8000/api/categories/engine-parts/products/
```

#### 4. Add to Cart (Session-based)
```bash
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=abc123..." \
  -d '{"product_id": 101, "quantity": 1}'
```

#### 5. View Cart
```bash
curl -X GET http://localhost:8000/api/cart/ \
  -H "Cookie: sessionid=abc123..."
```

#### 6. Create Order
```bash
curl -X POST http://localhost:8000/api/order/checkout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main St",
    "city": "Lagos",
    "phone_number": "+2348012345678"
  }'
```

#### 7. Initialize Payment
```bash
curl -X POST http://localhost:8000/api/payment/create/1/ \
  -H "Authorization: Bearer <access_token>"
```

#### 8. Verify Payment (after Paystack redirect)
```bash
curl -X GET "http://localhost:8000/api/payment/verify/?reference=ORD_1_a1b2c3d4e5" \
  -H "Authorization: Bearer <access_token>"
```

---

## Key Features

### Caching Strategy
- **Categories**: Cached for 1 hour
- **Products**: Cached per category/product for 1 hour
- Implemented using Django's cache framework (Redis)

### Stock Management
- Real-time stock checks before adding to cart
- Atomic transactions prevent overselling
- Stock **decremented** when order is placed
- Stock **incremented** when a refund is processed
- Prevents adding more than available stock

### Session-Based Cart
- No authentication required for browsing/cart operations
- Cart ID stored in session
- Automatically cleared after order creation
- Supports anonymous users

### Payment Integration
- Paystack payment gateway integration
- Payment references with unique identifiers
- Atomic payment verification with order updates
- Supports NGN currency

### Security Features
- JWT token-based authentication
- Transaction atomicity for critical operations
- Admin-only endpoints for product management
- Rate limiting (20 req/day anonymous, 70 req/day authenticated)
