# Utility function for file upload path
def get_upload_to(instance, filename):
    return f'products/{instance}/{filename}'
