from django.conf import settings
from django.contrib.auth import get_user_model, login


class DevAutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            settings.DEBUG
            and request.user.is_anonymous
            and request.get_host().split(':')[0] in {'127.0.0.1', 'localhost'}
        ):
            user_model = get_user_model()
            user, _ = user_model.objects.get_or_create(
                username='dev_browser_user'
            )
            if not user.has_usable_password():
                user.set_password('dev-browser-password')
                user.save(update_fields=['password'])
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return self.get_response(request)
