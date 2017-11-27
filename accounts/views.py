from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views import generic

from accounts.forms import UserProfileChangeForm
from core.models import Profile




class UserProfileChange(generic.FormView):
    form_class = UserProfileChangeForm
    template_name = 'registration/profile_change.html'

    def get_form_kwargs(self):
        kwargs = super(UserProfileChange, self).get_form_kwargs()
        kwargs["instance"] = Profile.objects.get(pk=self.request.user.pk)
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(UserProfileChange, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Your profile was updated.')
        return reverse('user_profile_change')