from celery import shared_task


@shared_task
def send_otp_to_phone_tasks(otp):
    print(f'Your OTP is: {otp}')


@shared_task
def send_otp_to_email_tasks(otp):
    print(f'Your OTP is: {otp}')
    #todo : send email
