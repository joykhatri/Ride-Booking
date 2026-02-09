from channels.db import database_sync_to_async

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.authentication import JWTAuthentication

        self.scope = dict(scope)
        query_string = scope.get("query_string", b"").decode()
        token = None
        if "token=" in query_string:
            token = query_string.split("token=")[1].split("&")[0]

        if token:
            try:
                jwt_auth = JWTAuthentication()
                validated = jwt_auth.get_validated_token(token)
                scope["user"] = await database_sync_to_async(jwt_auth.get_user)(validated)
            except Exception as e:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)