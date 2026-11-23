import resend

from backend.app.core.config import settings

resend.api_key = settings.RESEND_API_KEY

email = input("Enter your Resend account email: ").strip()

try:
    response = resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": [email],
        "subject": "Tone Neuron Email Test",
        "text": "Your Tone Neuron email service is working!",
    })

    print("SUCCESS:", response)

except Exception as error:
    print("FAILED")
    print("Error type:", type(error).__name__)
    print("Error message:", str(error))