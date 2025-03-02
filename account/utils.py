import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generateOtp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def sendOtpEmail(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP is: {otp}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
