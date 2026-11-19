import time

from django import forms
from django.core import signing

from catalog.models import Country
from core.i18n import t

from .models import ACTIVITY_CHOICES, VOLUME_CHOICES, Dealer, normalize_phone


class DealerForm(forms.ModelForm):
    consent = forms.BooleanField(required=True)
    website = forms.CharField(required=False)  # ловушка для ботов: человек это поле не видит
    ts = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Dealer
        fields = ["country", "city", "company", "contact_name", "phone", "email", "activity", "volume", "comment"]
        widgets = {"comment": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        f = self.fields
        f["country"].queryset = Country.objects.filter(is_active=True)
        f["country"].empty_label = t("form.choose")
        for name in ("country", "city", "company", "contact_name", "phone", "email", "activity", "volume", "comment"):
            f[name].label = t(f"form.{name}")
        f["activity"].choices = [("", t("form.choose"))] + [(k, t(f"activity.{k}")) for k, _ in ACTIVITY_CHOICES]
        f["volume"].choices = [("", t("form.choose"))] + [(k, t(f"volume.{k}")) for k, _ in VOLUME_CHOICES]
        f["phone"].widget.attrs.update({"placeholder": "+7 700 000 00 00", "inputmode": "tel", "autocomplete": "tel"})
        f["email"].widget.attrs.update({"placeholder": "name@company.com", "autocomplete": "email"})
        f["website"].widget.attrs.update({"tabindex": "-1", "autocomplete": "off"})
        if not self.is_bound:
            self.initial["ts"] = signing.dumps({"t": time.time()})

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not 7 <= len(normalize_phone(phone)) <= 15:
            raise forms.ValidationError(t("form.phone_invalid"))
        return phone
