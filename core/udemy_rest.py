from cloudscraper import create_scraper
from requests import Session
from bs4 import BeautifulSoup


class UdemySession:
    LOGIN_URL = "https://www.udemy.com/join/login-popup/?locale=en_US"
    MY_COURSES = "https://www.udemy.com/api-2.0/users/me/subscribed-courses/?ordering=-last_accessed&fields[course]=@min,enrollment_time,published_title,&fields[user]=@min&page=1&page_size=1000"
    SEARCH_URL = "https://www.udemy.com/api-2.0/shopping-carts/me/cart/"
    ADD_CART_URL = "https://www.udemy.com/api-2.0/shopping-carts/me/cart/"
    # POST {"buyables":[{"buyable_object_type":"course","id":3456530,"buyable_context":{}}]}
    ADD_DISCOUNT_URL = "https://www.udemy.com/api-2.0/shopping-carts/me/discounts/"
    # POST: {"codes":["4C2909E4D310F1B4FA41"]}
    CHECKOUT_URL = "https://www.udemy.com/payment/checkout-submit/"
    # POST {"checkout_event":"Submit","shopping_cart":{
    # "items":[{"discountInfo":{"code":"4C2909E4D310F1B4FA41"},"purchasePrice":{"amount":0,"currency":"EUR",
    # "price_string":"Free","currency_symbol":"€"},"buyableType":"course","buyableId":3456530,"buyableContext":{}}],
    # "is_cart":true},"payment_info":{"payment_vendor":"Free","payment_method":"free-method"},"tax_info":{
    # "is_tax_enabled":true,"tax_rate":21,"billing_location":{"country_code":"IE","secondary_location_info":null},
    # "currency_code":"eur","transaction_items":[{"udemy_txn_item_reference":"course-3456530",
    # "tax_included_amount":0,"tax_amount":0,"tax_excluded_amount":0}],"tax_breakdown_type":"tax_inclusive"}}

    HEADERS = {
        "Origin": "www.udemy.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
        "Accept": "*/*",
        "Accept-Encoding": None,
    }

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = Session()
        self.udemy_scraper = create_scraper()

    def login(self):
        response = self.udemy_scraper.get(self.LOGIN_URL)
        soup = BeautifulSoup(response.content, "html.parser")
        csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        _form_data = {"email": self.email, "password": self.password, "csrfmiddlewaretoken": csrf_token}
        self.udemy_scraper.headers.update({"Referer": self.LOGIN_URL})
        auth_response = self.udemy_scraper.post(self.LOGIN_URL, data=_form_data, allow_redirects=False)
        if auth_response.status_code != 302:
            raise Exception("Could not login")

        access_token = auth_response.cookies.get("access_token")
        bearer_token = f"Bearer {access_token}"
        self.session.headers = self.HEADERS
        self.session.headers.update({"Authorization": bearer_token, "X-Udemy-Authorization": bearer_token})
        self.session.cookies.update({"access_token": access_token})

    def my_courses(self):
        my_courses = self.session.get(self.MY_COURSES)
        return my_courses.json()

    def enroll(self, url, discount_code):
        course_id = self._get_course_id(url)
        self._add_to_cart(course_id)
        self._apply_discount(discount_code)

    def _get_course_id(self, url):
        response = self.session.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return int(soup.find("body")["data-clp-course-id"])

    def _add_to_cart(self, course_id):
        payload = {"buyables": [{"buyable_object_type": "course", "id": course_id, "buyable_context": {}}]}
        response = self.session.post(self.ADD_CART_URL, data=payload, allow_redirects=False)
        # TODO: Fix 412 response. Failed precondition
        print(response.status_code)

    def _apply_discount(self, discount_code):
        payload = {"codes": [discount_code]}
        response = self.session.post(self.ADD_DISCOUNT_URL, data=payload, allow_redirects=False)
        # TODO: Fix 412 response. Failed precondition
        print(response.status_code)


if __name__ == "__main__":
    us = UdemySession("test@mail.com", "goodpw")
    us.login()
    us.my_courses()
    us.enroll("https://www.udemy.com/course/advanced-mathematics-part-iii-statistics-probability", "SAM2612")
