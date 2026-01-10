# ALX Travel App 0x03 - Celery and RabbitMQ Integration

This project is a Django-based travel booking application with integrated Chapa Payment Gateway and background tasks using Celery and RabbitMQ.

## Features Added in 0x03
- **Asynchronous Tasks:** Integrated Celery with RabbitMQ as the message broker.
- **Email Notifications:** Implemented a background task to send booking confirmation emails automatically upon booking creation.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd alx_travel_app_0x03
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install Django djangorestframework requests python-dotenv celery drf_yasg
    ```

4.  **Install and Start RabbitMQ:**
    Follow the official [RabbitMQ installation guide](https://www.rabbitmq.com/download.html) for your operating system.
    Once installed, ensure it's running:
    ```bash
    # Linux example
    sudo service rabbitmq-server start
    ```

5.  **Database Migrations:**
    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

## Celery Configuration

The project is configured to use RabbitMQ. Celery settings can be found in `alx_travel_app/settings.py`:

```python
CELERY_BROKER_URL = 'pyamqp://localhost/'
CELERY_RESULT_BACKEND = 'rpc://'
```

### Running Celery Worker

To start the background worker, run the following command in a separate terminal:

```bash
celery -A alx_travel_app worker --loglevel=info
```

## Email Notifications

Booking confirmation emails are sent using the Django console email backend for development purposes. You can see the email content in the Celery worker's output.

To change to a real SMTP server, update `EMAIL_BACKEND` and provide SMTP settings in `settings.py`.

## API Endpoints

- **Bookings:** `/api/bookings/` (POST triggers the confirmation email task)
- **Listings:** `/api/listings/`
- **Payments:** `/api/listings/payment-initiate/`

## Swagger/Redoc Documentation

You can access the API documentation at:
*   Swagger UI: `http://127.0.0.1:8000/swagger/`
*   ReDoc: `http://127.0.0.1:8000/redoc/`

Happy coding! ✨# alx_travel_app_0x03
