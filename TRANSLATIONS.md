# Create or update the po files
./update_translations.sh

# Modify the po file in recipes/locale/<locale-name>/django.po

# Create or update the mo files
django-admin compilemessages
