#!/usr/bin/env python3
import asyncio
import logging.config


try:
    from core.scrapers.comidoc import ComidocScraper
except ModuleNotFoundError:
    from .core.scrapers.comidoc import ComidocScraper


def test_comidoc():
    """
    Check if we can scrape links successfully from comidoc.net

    :return:
    """
    try:
        logging.config.fileConfig(
            "logconfig.ini", disable_existing_loggers=False
        )
        cds = ComidocScraper(enabled=True, max_pages=1)

        loop = asyncio.get_event_loop()
        udemy_course_links = loop.run_until_complete(cds.run())

        if not udemy_course_links or len(udemy_course_links) == 0:
            raise AssertionError("No links scraped from comidoc. API may have changed")
    except Exception as e:
        print("Something went wrong while running comidoc test")
        raise e


if __name__ == "__main__":
    test_comidoc()
