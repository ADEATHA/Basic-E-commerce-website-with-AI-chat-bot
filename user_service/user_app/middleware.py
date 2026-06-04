from django.contrib.auth.models import AnonymousUser

class RoleBasedSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            # Nếu đang ở khu vực khách hàng nhưng lại là nhân viên -> Ẩn trạng thái đăng nhập
            if (path.startswith('/customer/') or path == '/') and request.user.is_staff:
                request.user = AnonymousUser()
            
            # Nếu đang ở khu vực nhân viên nhưng không phải nhân viên -> Ẩn trạng thái đăng nhập
            elif path.startswith('/staff/') and not request.user.is_staff:
                request.user = AnonymousUser()
                
        response = self.get_response(request)
        return response
