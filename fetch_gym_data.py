#!/usr/bin/env uv run
# /// script
# dependencies = [
#   "playwright",
#   "python-dotenv",
#   "icalendar",
# ]
# ///
"""
Standalone gym data fetcher.
Logs in, scrapes class schedule, writes .ics to ics_files/.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv

from gym_calendar.ical import filter_classes, classes_to_ical
from gym_calendar.scraper import (
	ensure_authenticated, navigate_to_gym, extract_classes_from_page,
)

load_dotenv()
USERNAME = os.getenv("METROPOLITAN_USER")
PASSWORD = os.getenv("METROPOLITAN_PASS")


async def fetch_gym_classes(headless=True):
	print("Fetching gym class data...")

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=headless, slow_mo=100 if not headless else 0)
		context = await browser.new_context()
		await ensure_authenticated(context, USERNAME, PASSWORD)

		page = await context.new_page()
		await navigate_to_gym(page)

		print("  Extracting class data...")
		all_classes = await extract_classes_from_page(page)
		print(f"  Found {len(all_classes)} total classes")

		now = datetime.now(timezone.utc).replace(tzinfo=None)
		future_classes = [
			cls for cls in all_classes
			if cls.get("HoraFin") and datetime.fromisoformat(cls["HoraFin"]) >= now
		]
		print(f"  {len(future_classes)} future classes")

		filtered_classes = filter_classes(future_classes)
		print(f"  {len(filtered_classes)} classes match filters")

		# Save raw JSON
		json_path = Path(__file__).parent / "data" / "extracted_classes.json"
		json_path.parent.mkdir(parents=True, exist_ok=True)
		with open(json_path, "w", encoding="utf-8") as f:
			json.dump(filtered_classes, f, indent=2, ensure_ascii=False)
		print(f"  Saved JSON to {json_path}")

		output_file = "ics_files/metropolitan_classes.ics"
		event_count = classes_to_ical(filtered_classes, output_file)
		print(f"  Created {output_file} with {event_count} events")

		await browser.close()

		return {
			"total": len(all_classes),
			"future": len(future_classes),
			"filtered": len(filtered_classes),
			"events_created": event_count,
		}


if __name__ == "__main__":
	result = asyncio.run(fetch_gym_classes(headless=False))
	print(f"\nComplete!")
	print(f"  Total: {result['total']}")
	print(f"  Future: {result['future']}")
	print(f"  Filtered: {result['filtered']}")
	print(f"  Events: {result['events_created']}")
