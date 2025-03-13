import pyotp
from django.core.cache import cache

OTP_TIMEOUT = 120

def _get_totp(secret):
    """Returns a TOTP object for the given secret."""
    return pyotp.TOTP(secret)

def _store_secret(user_id, secret, prefix='otp_secret'):
    """Store the OTP secret in the cache."""
    cache.set(f'{prefix}_{user_id}', secret, timeout=OTP_TIMEOUT)

def _retrieve_secret(user_id, prefix='otp_secret'):
    """Retrieve the OTP secret from the cache."""
    return cache.get(f'{prefix}_{user_id}')


def generate_otp(user_id, prefix='otp_secret'):
    """Generate a one-time password (OTP) and store its secret."""
    delete_otp(user_id, prefix)

    secret = pyotp.random_base32()
    _store_secret(user_id, secret, prefix)
    
    totp = _get_totp(secret)
    return totp.now()

def verify_otp(user_id, otp, prefix='otp_secret'):
    """Verify the provided OTP against the stored secret."""
    secret = _retrieve_secret(user_id, prefix)
    if secret is None:
        return False

    totp = _get_totp(secret)
    if totp.verify(otp):
        delete_otp(user_id, prefix)
        return True

    return False

def delete_otp(user_id, prefix='otp_secret'):
    """Delete the stored OTP secret from the cache."""
    cache.delete(f'{prefix}_{user_id}')



def generate_otp_pass(user_id):
    return generate_otp(user_id, prefix='otp_secret_pass')

def verify_otp_pass(user_id, otp):
    return verify_otp(user_id, otp, prefix='otp_secret_pass')

def delete_otp_pass(user_id):
    delete_otp(user_id, prefix='otp_secret_pass')


def generate_otp_change_pass(user_id):
    return generate_otp(user_id, prefix='otp_secret_change_pass')

def verify_otp_change_pass(user_id, otp):
    return verify_otp(user_id, otp, prefix='otp_secret_change_pass')

def delete_otp_change_pass(user_id):
    delete_otp(user_id, prefix='otp_secret_change_pass')


def generate_otp_change_number(user_id):
    return generate_otp(user_id, prefix='otp_secret_change_number')

def verify_otp_change_number(user_id, otp):
    return verify_otp(user_id, otp, prefix='otp_secret_change_number')

def delete_otp_change_number(user_id):
    delete_otp(user_id, prefix='otp_secret_change_number')


def generate_otp_change_email(user_id):
    return generate_otp(user_id, prefix='otp_secret_change_email')

def verify_otp_change_email(user_id, otp):
    return verify_otp(user_id, otp, prefix='otp_secret_change_email')

def delete_otp_change_email(user_id):
    delete_otp(user_id, prefix='otp_secret_change_email')
