from django.test import TestCase, RequestFactory
from .views import home_page


class home_page_TestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_request_for_self(self):
        request = self.factory.post('/home', {"needs_access": "myeslf"})
        response = home_page.as_view()(request)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/user-end/?behalf=False')
