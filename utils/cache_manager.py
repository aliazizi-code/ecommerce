from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation

class CacheManager:
    @staticmethod
    def set_new_value(user_id, value, key_name, timeout):
        try:
            CacheManager.delete_value(user_id, key_name)
            success = cache.set(f"{key_name}_{user_id}", str(value), timeout=timeout)
            if not success:
                raise SuspiciousOperation("Failed to set the cache value.")
        except Exception as e:
            print(f"Error setting cache value: {e}")

    @staticmethod
    def get_value(user_id, key_name):
        try:
            value = cache.get(f"{key_name}_{user_id}")
            if value is None:
                print("Value not found in cache.")
            return value
        except Exception as e:
            print(f"Error getting cache value: {e}")
            return None

    @staticmethod
    def delete_value(user_id, key_name):
        try:
            cache.delete(f"{key_name}_{user_id}")
        except Exception as e:
            print(f"Error deleting cache value: {e}")