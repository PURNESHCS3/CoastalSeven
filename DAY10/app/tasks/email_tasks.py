import smtplib
from email.mime.text import MIMEText

from app.celery_app import celery
from app.database import settings


@celery.task(
    name="app.tasks.email_tasks.send_order_confirmation_email"
)
def send_order_confirmation_email(
    email: str,
    order_id: int,
    total_amount: float
):

    message = MIMEText(
        f"""
Hello,

Your order #{order_id} has been successfully placed.

Order Total: ₹{total_amount:.2f}

Thank you for shopping with us.

Regards,
E-Commerce Team
"""
    )

    message["Subject"] = f"Order Confirmation #{order_id}"
    message["From"] = settings.SMTP_USERNAME
    message["To"] = email

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT
    ) as server:

        server.starttls()

        server.login(
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD
        )

        server.send_message(message)

    return {
        "message": "Order confirmation email sent",
        "order_id": order_id,
        "email": email
    }