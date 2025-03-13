from django.core.cache import cache


class CacheManager:
    @staticmethod
    def set_new_value(user_id, value, key_name, timeout):
        CacheManager.delete_value(user_id, key_name)
        cache.set(f"{key_name}_{user_id}", value, timeout=timeout)

    @staticmethod
    def get_value(user_id, key_name):
        cache.get(f"{key_name}_{user_id}")

    @staticmethod
    def delete_value(user_id, key_name):
        cache.delete(f"{key_name}_{user_id}")
