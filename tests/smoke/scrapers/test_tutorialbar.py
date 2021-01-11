#!/usr/bin/env python3
import asyncio
import logging.config

try:
    from core.scrapers.tutorialbar import TutorialBarScraper
except ModuleNotFoundError:
    from .core.scrapers.tutorialbar import TutorialBarScraper


def test_tutorialbar():
    """
    Check if we can scrape links successfully from tutorialbar.com

    :return:
    """
    try:
        logging.config.fileConfig(
            "logconfig.ini", disable_existing_loggers=False
        )
        tbs = TutorialBarScraper(enabled=True, max_pages=1)

        loop = asyncio.get_event_loop()
        udemy_course_links = loop.run_until_complete(tbs.run())

        if not udemy_course_links or len(udemy_course_links) == 0:
            raise AssertionError(
                "No links scraped from tutorialbar. API may have changed"
            )
    except Exception as e:
        print("Something went wrong while running tutorialbar test")
        raise e


if __name__ == "__main__":
    test_tutorialbar()
