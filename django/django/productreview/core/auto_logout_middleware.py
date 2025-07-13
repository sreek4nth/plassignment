from django.contrib.auth import logout

class AutoLogoutOnRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated and request.method == 'GET':
            logout(request)
        response = self.get_response(request)
        return response
