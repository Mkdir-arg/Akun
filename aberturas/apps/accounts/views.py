from django.contrib.auth.views import LoginView

class AkunLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        resp = super().form_valid(form)
        remember = self.request.POST.get("remember_me") in ("on", "true", "1")
        self.request.session.set_expiry(60*60*24*14 if remember else 0)
        return resp