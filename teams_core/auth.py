from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        print("CSRF check bypassed")  # Debugging line
        # No operation, effectively bypassing CSRF check
        return

    #pass
