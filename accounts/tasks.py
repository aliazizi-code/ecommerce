from celery import shared_task
from core.celery import app


@app.task
def send_otp_to_phone_tasks(otp):
    print(f'Your OTP is: {otp}')


@app.task
def send_otp_to_email_tasks(otp):
    print(f'Your OTP is: {otp}')
    #todo : send email
