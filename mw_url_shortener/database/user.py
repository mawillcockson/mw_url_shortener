print(f"imported mw_url_shortener.database.user as {__name__}")
"""
This file exists purely to export an organized namespace
"""
from .models import UserModel as Model
from .interface import get_user as get, create_user as create, delete_user as delete, update_user as update, list_users as list
