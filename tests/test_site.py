"""Проверка обязательных сценариев приёмки из ТЗ."""
import re
from decimal import Decimal
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from catalog.models import Country, Price, PriceHistory, Product
from core import i18n
from core.models import SiteSettings
from crm import bitrix, services
from crm.models import CrmJob
from dealers.models import Dealer
from orders import calc
from orders.models import Order

FORM = {"city": "Алматы", "company": "ТОО Тест", "contact_name": "Иван", "phone": "+7 700 111 22 33",
        "email": "a@example.com", "consent": "on", "website": ""}


def fake_bitrix(calls, fail=None):
    """Имитация REST Bitrix24: запоминает вызовы, при необходимости падает на заданном методе."""
    def call(method, params=None):
        calls.append((method, params or {}))
        if fail and method in fail:
            raise bitrix.BitrixError(f"{method}: сбой")
        return {"crm.duplicate.findbycomm": [], "crm.lead.add": 501, "crm.lead.get": {"STATUS_ID": "NEW"},
                "tasks.task.add": {"task": {"id": 77}}, "tasks.task.get": {"task": {"status": "2"}}}.get(method, True)
    return call


@override_settings(FORM_MIN_SECONDS=0, AXES_ENABLED=False, BITRIX24_WEBHOOK_URL="https://example.invalid/rest/1/x")
class SiteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("init_site", demo=True, verbosity=0)

    def setUp(self):
        cache.clear()
        i18n.invalidate()
        self.calls = []
        patcher = mock.patch("crm.bitrix.call", side_effect=fake_bitrix(self.calls))
        self.bitrix = patcher.start()
        self.addCleanup(patcher.stop)

    def register(self, country="kz", **extra):
        page = self.client.get("/ru/become-distributor/")
        data = {**FORM, "country": Country.objects.get(code=country).pk, "ts": page.context["form"].initial["ts"], **extra}
        return self.client.post("/ru/become-distributor/", data)

    # --- языки -------------------------------------------------------------
    def test_language_switch(self):
        ru, en = self.client.get("/ru/"), self.client.get("/en/")
        self.assertContains(ru, "Стать дистрибьютором")
        self.assertContains(en, "Become a distributor")
        self.assertContains(ru, 'hreflang="en" href="http://testserver/en/"')
        self.assertContains(self.client.get("/en/catalog/chili-50/"), "hot chili")

    def test_all_template_keys_have_translations(self):
        used = set()
        for path in Path(settings.BASE_DIR, "templates").glob("*.html"):
            used |= set(re.findall(r'{% t "([a-z0-9_.]+)"', path.read_text()))
        missing = {k for k in used if k not in i18n.STRINGS and not k.endswith(".")}
        self.assertFalse(missing)
        self.assertTrue(all(v["ru"] and v["en"] for v in i18n.STRINGS.values()))

    def test_admin_can_override_ui_text(self):
        from core.models import UiText
        UiText.objects.update_or_create(key="cta.become", defaults={"text_ru": "Хочу продавать MAZZAA"})
        i18n.invalidate()
        self.assertContains(self.client.get("/ru/"), "Хочу продавать MAZZAA")

    # --- закрытые цены -----------------------------------------------------
    def test_visitor_does_not_see_prices(self):
        price = Price.objects.get(product__slug="chili-50", country__code="kz")
        self.assertRedirects(self.client.get("/ru/prices/"), "/ru/become-distributor/?next=/ru/prices/")
        for url in ("/ru/catalog/", "/ru/catalog/chili-50/", "/ru/calculator/"):
            self.assertNotContains(self.client.get(url), f"{price.price:,.2f}".replace(",", " "))
        data = self.client.post("/api/calc/", {"items": [{"id": price.product_id, "boxes": 5}]},
                                content_type="application/json").json()
        self.assertFalse(data["has_prices"])
        self.assertIsNone(data["lines"][0]["price"])
        self.assertIsNone(data["total_amount"])
        self.assertEqual(self.client.get("/ru/prices/download.xlsx").status_code, 302)

    # --- анкета -> лид, задача, цены своей страны ---------------------------
    def test_registration_creates_lead_task_and_opens_country_prices(self):
        self.client.get("/ru/?utm_source=google&utm_medium=cpc&utm_campaign=kz-chips&gclid=abc")
        response = self.register()
        self.assertRedirects(response, "/ru/prices/")
        dealer = Dealer.objects.get()
        self.assertEqual((dealer.utm_source, dealer.utm_campaign, dealer.click_id), ("google", "kz-chips", "abc"))
        self.assertEqual((dealer.bitrix_lead_id, dealer.bitrix_task_id), (501, 77))
        lead = dict(self.calls)["crm.lead.add"]["fields"]
        self.assertEqual(lead["UTM_SOURCE"], "google")
        self.assertEqual(lead["ADDRESS_COUNTRY"], "Казахстан")
        task = dict(self.calls)["tasks.task.add"]["fields"]
        self.assertIn("Связаться с новым потенциальным дилером MAZZAA", task["TITLE"])
        self.assertEqual(task["UF_CRM_TASK"], ["L_501"])
        self.assertEqual(CrmJob.objects.get().status, CrmJob.DONE)
        page = self.client.get("/ru/prices/")
        self.assertContains(page, "KZT")
        self.assertNotContains(page, "RUB")
        self.assertContains(page, "2 808,00".replace(",", "."))
        self.assertEqual(self.client.get("/ru/prices/download.xlsx").status_code, 200)
        self.assertEqual(self.client.get("/ru/prices/download.pdf")["Content-Type"], "application/pdf")

    def test_repeat_registration_does_not_duplicate_lead(self):
        self.register()
        self.client.session.flush()
        self.register(company="ТОО Тест 2")
        self.assertEqual(Dealer.objects.count(), 1)
        self.assertEqual([m for m, _ in self.calls].count("crm.lead.add"), 1)

    def test_existing_bitrix_lead_is_reused(self):
        self.bitrix.side_effect = lambda m, p=None: (
            self.calls.append((m, p)) or {"crm.duplicate.findbycomm": {"LEAD": [40, 41]},
                                          "tasks.task.add": {"task": {"id": 9}}}.get(m, True))
        self.register()
        self.assertEqual(Dealer.objects.get().bitrix_lead_id, 41)
        self.assertNotIn("crm.lead.add", [m for m, _ in self.calls])

    def test_manual_approval_mode(self):
        s = SiteSettings.load()
        s.price_access_mode = s.ACCESS_MANUAL
        s.save()
        self.assertRedirects(self.register(), "/ru/become-distributor/pending/")
        self.assertRedirects(self.client.get("/ru/prices/"), "/ru/become-distributor/pending/")
        self.assertTrue(CrmJob.objects.filter(kind=CrmJob.LEAD).exists())  # лид создаётся и без доступа
        Dealer.objects.update(status=Dealer.APPROVED)
        self.assertEqual(self.client.get("/ru/prices/").status_code, 200)

    def test_spam_protection(self):
        page = self.client.get("/ru/become-distributor/")
        data = {**FORM, "country": Country.objects.get(code="kz").pk, "ts": page.context["form"].initial["ts"]}
        self.client.post("/ru/become-distributor/", {**data, "website": "http://spam"})
        self.client.post("/ru/become-distributor/", {**data, "ts": "forged"})
        with override_settings(FORM_MIN_SECONDS=30):
            self.client.post("/ru/become-distributor/", data)
        self.assertEqual(Dealer.objects.count(), 0)

    # --- калькулятор -------------------------------------------------------
    def test_calculator_math(self):
        kz = Country.objects.get(code="kz")
        a, b = Product.objects.get(slug="sticks-40"), Product.objects.get(slug="cheese-100")
        result = calc.calculate({a.pk: 120, b.pk: 800}, kz)
        self.assertEqual(result["total_amount"], 120 * Decimal("4992") + 800 * Decimal("3432"))
        self.assertEqual(result["total_boxes"], 920)
        self.assertEqual(result["total_weight_kg"], Decimal("1568.00"))        # 120×2.4 + 800×1.6
        self.assertEqual(result["total_volume_m3"], Decimal("31.200"))         # 120×0.036 + 800×0.0336
        self.assertEqual(result["pallets"], 15)                                # 120/60 + 800/64 = 14.5
        self.assertEqual(result["containers"]["20"]["count"], 2)
        self.assertEqual(result["containers"]["40"]["count"], 1)

    def test_container_fit_uses_box_dimensions_and_weight_limit(self):
        self.assertEqual(calc.boxes_fit((40, 30, 30), calc.CONTAINERS["20"]["dims"]), 14 * 7 * 7)
        heavy = Product.objects.get(slug="chili-50")
        heavy.gross_weight_kg = Decimal("60")
        heavy.save()
        result = calc.calculate({heavy.pk: 600}, None)
        self.assertEqual(result["containers"]["20"]["limited_by"], "weight")
        self.assertEqual(result["containers"]["20"]["count"], 2)               # 36 т при лимите 28,2 т

    def test_hidden_price_is_excluded(self):
        kz = Country.objects.get(code="kz")
        p = Product.objects.get(slug="chili-50")
        Price.objects.filter(product=p, country=kz).update(is_hidden=True)
        self.assertEqual(calc.calculate({p.pk: 3}, kz)["lines"], [])
        self.register()
        self.assertNotContains(self.client.get("/ru/prices/"), "острого чили</a></td>\n      <td>50<")

    def test_150g_without_packs_per_box_still_calculates(self):
        p = Product.objects.get(slug="chili-150")
        self.assertIsNone(p.packs_per_box)
        line = calc.calculate({p.pk: 2}, Country.objects.get(code="ru"))["lines"][0]
        self.assertIsNone(line["packs"])
        self.assertEqual(line["amount"], 2 * Decimal("810"))

    # --- заказ -------------------------------------------------------------
    def test_order_is_saved_with_server_prices_and_sent_to_crm(self):
        self.register()
        p = Product.objects.get(slug="chili-50")
        items = '[{"id": %d, "boxes": 10, "price": 1}]' % p.pk                  # подмена цены клиентом игнорируется
        response = self.client.post("/ru/order/submit/", {"items": items, "comment": "Срочно"})
        order = Order.objects.get()
        self.assertRedirects(response, f"/ru/order/{order.number}/")
        self.assertEqual((order.total_amount, order.currency), (Decimal("28080.00"), "KZT"))
        self.assertEqual(order.items.get().price, Decimal("2808.00"))
        methods = [m for m, _ in self.calls]
        self.assertEqual(methods.count("crm.lead.add"), 1)                     # заказ идёт в существующий лид
        comment = [p for m, p in self.calls if m == "crm.timeline.comment.add"][-1]["fields"]
        self.assertEqual((comment["ENTITY_ID"], comment["ENTITY_TYPE"]), (501, "lead"))
        self.assertIn(order.number, comment["COMMENT"])
        self.assertIn("im.notify.system.add", methods)
        self.assertEqual(methods.count("tasks.task.add"), 2)
        Price.objects.filter(product=p).update(price=1)                        # цена в заказе зафиксирована
        self.assertEqual(Order.objects.get().items.get().price, Decimal("2808.00"))
        self.assertContains(self.client.get(f"/ru/order/{order.number}/"), order.number)
        self.assertEqual(self.client.get(f"/ru/order/{order.number}/offer.pdf").status_code, 200)
        self.assertEqual(self.client.post("/ru/calculator/offer.xlsx", {"items": items}).status_code, 200)

    def test_order_of_another_dealer_is_not_visible(self):
        self.register()
        p = Product.objects.get(slug="chili-50")
        self.client.post("/ru/order/submit/", {"items": '[{"id": %d, "boxes": 1}]' % p.pk})
        number = Order.objects.get().number
        self.client.session.flush()
        self.assertEqual(self.client.get(f"/ru/order/{number}/").status_code, 404)

    # --- надёжность передачи в CRM -----------------------------------------
    def test_crm_failure_is_logged_and_retried(self):
        self.bitrix.side_effect = fake_bitrix(self.calls, fail={"crm.lead.add"})
        self.assertRedirects(self.register(), "/ru/prices/")                   # клиент ошибки не видит
        job = CrmJob.objects.get()
        self.assertEqual((job.status, job.attempts), (CrmJob.PENDING, 1))
        self.assertIn("crm.lead.add", job.last_error)
        self.bitrix.side_effect = fake_bitrix(self.calls)
        CrmJob.objects.update(next_attempt_at=timezone.now())
        self.assertEqual(services.process_queue(), 1)
        self.assertEqual(Dealer.objects.get().bitrix_lead_id, 501)

    def test_without_webhook_requests_are_kept(self):
        with override_settings(BITRIX24_WEBHOOK_URL=""):
            self.register()
        job = CrmJob.objects.get()
        self.assertEqual((job.status, job.attempts), (CrmJob.PENDING, 0))
        self.assertEqual(self.calls, [])

    def test_overdue_task_notifies_head(self):
        self.register()
        s = SiteSettings.load()
        s.bitrix_head_id = 5
        s.save()
        Dealer.objects.update(task_deadline=timezone.now() - timezone.timedelta(hours=2))
        self.assertEqual(bitrix.check_overdue(s), 1)
        self.assertEqual(self.calls[-1][1]["USER_ID"], 5)
        self.assertEqual(bitrix.check_overdue(s), 0)                           # повторно не уведомляем

    def test_deadline_respects_working_hours(self):
        s = SiteSettings.load()
        friday_evening = timezone.make_aware(timezone.datetime(2026, 11, 20, 17, 30))
        deadline = bitrix.add_working_minutes(friday_evening, 60, s)
        self.assertEqual(timezone.localtime(deadline).strftime("%a %H:%M"), "Mon 09:30")

    # --- админ-панель ------------------------------------------------------
    def test_admin_changes_price_and_history_is_recorded(self):
        admin = User.objects.create_superuser("root", "r@example.com", "S3cure-pass-123")
        self.client.force_login(admin)
        price = Price.objects.get(product__slug="chili-50", country__code="kz")
        response = self.client.post(f"/admin/catalog/price/{price.pk}/change/", {
            "product": price.product_id, "country": price.country_id, "price": "3000.00"})
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        self.register()
        self.assertContains(self.client.get("/ru/prices/"), "3 000.00")
        history = PriceHistory.objects.filter(product=price.product, country=price.country).first()
        self.assertEqual((history.old_price, history.new_price, history.changed_by), (Decimal("2808.00"), Decimal("3000.00"), admin))

    # --- SEO, аналитика, защита файлов -------------------------------------
    def test_seo_and_analytics(self):
        self.assertContains(self.client.get("/robots.txt"), "Sitemap:")
        sitemap = self.client.get("/sitemap.xml")
        self.assertContains(sitemap, "/en/catalog/chili-50/")
        self.assertContains(sitemap, 'hreflang="ru"')
        s = SiteSettings.load()
        s.gtm_id, s.meta_pixel_id = "GTM-TEST", "123"
        s.save()
        self.assertContains(self.client.get("/ru/"), '"gtm": "GTM-TEST"')
        self.register()
        self.assertContains(self.client.get("/ru/prices/"), '"event": "generate_lead"')
        self.assertContains(self.client.get("/ru/markets/kz/"), "Казахстан")
        self.assertEqual(self.client.get("/ru/markets/md/").status_code, 404)

    def test_protected_media_is_not_public(self):
        self.assertEqual(self.client.get("/media/protected/marketing/file.pdf").status_code, 404)
