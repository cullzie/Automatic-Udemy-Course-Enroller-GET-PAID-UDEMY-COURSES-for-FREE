import asyncio
import logging
from typing import List
from urllib.parse import unquote

from bs4 import BeautifulSoup

from udemy_enroller.http import get
from udemy_enroller.scrapers.base_scraper import BaseScraper

logger = logging.getLogger("udemy_enroller")


class IDownloadCouponScraper(BaseScraper):
    """
    Contains any logic related to scraping of data from tutorialbar.com
    """

    DOMAIN = "https://idownloadcoupon.com"

    def __init__(self, enabled, max_pages=None):
        super().__init__()
        self.scraper_name = "idownloadcoupon"
        if not enabled:
            self.set_state_disabled()
        self.last_page = None
        self.max_pages = max_pages

    @BaseScraper.time_run
    async def run(self) -> List:
        """
        Runs the steps to scrape links from tutorialbar.com

        :return: list of udemy coupon links
        """
        links = await self.get_links()
        self.max_pages_reached()
        return links

    async def get_links(self) -> List:
        """
        Scrape udemy links from tutorialbar.com

        :return: List of udemy course urls
        """
        self.current_page += 1
        course_links = await self.get_course_links(
            f"{self.DOMAIN}/category/paid-now-free-udemy-promo-code/page/{self.current_page}/"
        )

        logger.info(
            f"Page: {self.current_page} of {self.last_page} scraped from idownloadcoupon.com"
        )
        udemy_links = await self.gather_udemy_course_links(course_links)

        for counter, course in enumerate(udemy_links):
            logger.info(f"Received Link {counter + 1} : {course}")

        return udemy_links

    async def get_course_links(self, url: str) -> List:
        """
        Gets the url of pages which contain the udemy link we want to get

        :param str url: The url to scrape data from
        :return: list of pages on tutorialbar.com that contain Udemy coupons
        """
        text = await get(url)
        if text is not None:
            soup = BeautifulSoup(text.decode("utf-8"), "html.parser")

            links = soup.find_all("h2")
            course_links = [link.find("a").get("href") for link in links]

            self.last_page = int(
                soup.find("a", class_="next page-numbers")
                .find_previous_sibling()
                .text.replace(",", "")
            )

            return course_links

    @staticmethod
    async def get_udemy_course_links(url: str) -> List:
        """
        Gets the udemy course link

        :param str url: The url to scrape data from
        :return: Coupon link of the udemy course
        """
        links = list()
        text = await get(url)
        if text is not None:
            soup = BeautifulSoup(text.decode("utf-8"), "html.parser")
            link = soup.find("a", class_="coupon-code-link btn promotion") or soup.find(
                "a", string="Enroll Now"
            )
            udemy_link = link.get("href") if link is not None else None
            if udemy_link is not None:
                udemy_url = "https://www.udemy.com"
                if not udemy_link.startswith(udemy_url):
                    links.append(
                        f"{udemy_url}{unquote(udemy_link).split(udemy_url)[1]}"
                    )
            else:
                for link_element in soup.find_all(
                    "div",
                    class_="public-DraftStyleDefault-block public-DraftStyleDefault-ltr",
                ):
                    if link_element.find("a"):
                        links.append((link_element.find("a").get("href")))

            return links


if __name__ == "__main__":
    idcs = IDownloadCouponScraper(enabled=True, max_pages=5)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(idcs.run())
