# Deployment Guide for ALX Travel App

This document provides instructions for deploying the ALX Travel App to a cloud hosting provider like Render.

## Prerequisites

- A free account on a cloud provider (e.g., Render).
- `git` installed and configured on your local machine.
- Your project pushed to a GitHub repository.

## Deployment Steps (Render Example)

1.  **Create a New Web Service:**
    *   In your Render dashboard, click "New +" and select "Web Service".
    *   Connect your GitHub repository where `alx_travel_app_0x03` is located.

2.  **Configure the Web Service:**
    *   **Name:** Give your service a name (e.g., `alx-travel-app`).
    *   **Root Directory:** Leave this blank if `requirements.txt` is in your repository's root. If your project is in a subdirectory, enter the path (e.g., `repos/alx_travel_app_0x03`).
    *   **Environment:** `Python 3`
    *   **Region:** Choose a region close to you.
    *   **Build Command:** `bash build.sh`
    *   **Start Command:** `gunicorn alx_travel_app.wsgi`

3.  **Add a Redis Instance:**
    *   Click "New +" and select "Redis".
    *   Give it a name and select a plan.
    *   Copy the "Internal Redis URL" provided.

4.  **Add a Celery Worker:**
    *   Click "New +" and select "Background Worker".
    *   Give it a name (e.g., `celery-worker`).
    *   **Start Command:** `celery -A alx_travel_app.celery worker -l info`
    *   You will need to set the same environment variables for this worker as for the web service.

5.  **Configure Environment Variables:**
    *   Go to the "Environment" tab for both your Web Service and your Background Worker.
    *   Add the following environment variables:
        *   `SECRET_KEY`: Generate a new Django secret key for production.
        *   `DEBUG`: `False`
        *   `ALLOWED_HOSTS`: The URL of your deployed application (e.g., `alx-travel-app.onrender.com`).
        *   `DATABASE_URL`: The external URL of the PostgreSQL database provided by Render (or your own).
        *   `CELERY_BROKER_URL`: The internal Redis URL you copied in Step 3.

6.  **Deploy:**
    *   Click "Create Web Service". Render will automatically build and deploy your application.
    *   The first build may take a few minutes. Check the logs for any errors.

## Post-Deployment Checks

1.  **Swagger Documentation:**
    *   Navigate to `https://<your-app-url>.onrender.com/swagger/`.
    *   The API documentation should be publicly accessible.

2.  **Test Endpoints:**
    *   Use the Swagger UI or a tool like Postman to test your API endpoints.
    *   Ensure the booking endpoint triggers the email notification (check the Celery worker logs).

3.  **Celery Worker:**
    *   Check the logs for your Celery worker in the Render dashboard to ensure it's running and processing tasks correctly.
