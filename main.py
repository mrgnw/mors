#!/usr/bin/env uv run
# /// script
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "icalendar",
#   "playwright",
#   "python-dotenv",
# ]
# ///
"""
FastAPI iCalendar server that:
1. Fetches gym class data from Metropolitan website on startup
2. Merges .ics files, filters to future events, serves via HTTP
3. Supports optional ?alert=N query param for reminders

Usage:
    uv run main.py

Subscribe to: http://localhost:3083/calendar.ics
With alerts:  http://localhost:3083/calendar.ics?alert=25
"""

from fastapi import FastAPI, Query, Response, BackgroundTasks
from fastapi.responses import PlainTextResponse
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Alarm
import asyncio
import os
import uvicorn
from dotenv import load_dotenv

from gym_calendar.config import ICS_DIR, CONSOLIDATED_FILE
from gym_calendar.ical import filter_classes, classes_to_ical

# Import scraper (Playwright optional for environments without it)
scraper_available = False
try:
	from gym_calendar.scraper import (
		check_cookies_valid, ensure_authenticated,
		navigate_to_gym, extract_classes_from_page,
	)
	from playwright.async_api import async_playwright
	scraper_available = True
except ImportError:
	pass

load_dotenv()

app = FastAPI(title="Gym Calendar Server", docs_url=None, redoc_url=None)

USERNAME = os.getenv("METROPOLITAN_USER")
PASSWORD = os.getenv("METROPOLITAN_PASS")

last_fetch_time = None
fetch_in_progress = False


def is_future_event(event):
	"""Check if an ical VEVENT is today or in the future."""
	today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

	dtstart = event.get('DTSTART')
	if dtstart is None:
		return True

	dt = dtstart.dt
	if isinstance(dt, datetime):
		event_date = dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
	else:
		event_date = datetime.combine(dt, datetime.min.time())

	return event_date >= today


def merge_and_filter_ics_files(reminder_minutes=None):
	"""Merge all .ics files, filter to future events, optionally add alarms."""
	ICS_DIR.mkdir(exist_ok=True)
	ics_files = list(ICS_DIR.glob("*.ics"))

	if not ics_files:
		print(f"No .ics files found in {ICS_DIR}")
		return None

	print(f"Found {len(ics_files)} .ics file(s)")

	merged_cal = Calendar()
	merged_cal.add('prodid', '-//Gym Calendar Server//EN')
	merged_cal.add('version', '2.0')
	merged_cal.add('method', 'PUBLISH')
	merged_cal.add('calscale', 'GREGORIAN')
	merged_cal.add('x-wr-calname', 'Gym Classes')
	merged_cal.add('x-wr-timezone', 'Europe/Madrid')

	future_events_count = 0
	seen_uids = set()

	for ics_file in ics_files:
		try:
			cal = Calendar.from_ical(ics_file.read_bytes())
			for component in cal.walk():
				if component.name != "VEVENT":
					continue
				uid = str(component.get('uid', ''))
				if uid in seen_uids:
					continue
				seen_uids.add(uid)
				if not is_future_event(component):
					continue

				# Strip existing alarms, add new one if requested
				component.subcomponents = [
					c for c in component.subcomponents if c.name != "VALARM"
				]
				if reminder_minutes is not None:
					alarm = Alarm()
					alarm.add('action', 'DISPLAY')
					alarm.add('trigger', timedelta(minutes=-reminder_minutes))
					summary = str(component.get('summary', 'Class'))
					alarm.add('description', f'{summary} starts in {reminder_minutes} minutes')
					component.add_component(alarm)

				merged_cal.add_component(component)
				future_events_count += 1

		except Exception as e:
			print(f"  Error reading {ics_file.name}: {e}")
			continue

	if future_events_count == 0:
		print("No future events found")
		return None

	# Delete individual files, keep consolidated
	for ics_file in ics_files:
		if ics_file.name != CONSOLIDATED_FILE:
			ics_file.unlink()

	consolidated_path = ICS_DIR / CONSOLIDATED_FILE
	ics_content = merged_cal.to_ical()
	consolidated_path.write_bytes(ics_content)
	print(f"Wrote {future_events_count} event(s) to {CONSOLIDATED_FILE}")

	return ics_content


async def fetch_gym_classes_background():
	"""Background task to fetch gym classes."""
	global last_fetch_time, fetch_in_progress

	if not scraper_available:
		print("Playwright not available, skipping fetch")
		return
	if fetch_in_progress:
		print("Fetch already in progress, skipping")
		return

	fetch_in_progress = True
	try:
		print("\nFetching gym class data...")

		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=True)
			context = await browser.new_context()
			await ensure_authenticated(context, USERNAME, PASSWORD)

			page = await context.new_page()
			await navigate_to_gym(page)

			print("  Extracting class data for multiple weeks...")
			all_classes = []
			today = datetime.now()

			for week_offset in range(2):
				week_date = today + timedelta(weeks=week_offset)
				date_str = week_date.strftime("%Y-%m-%dT00:00:00")
				url = (
					f"https://clubmetropolitan.provis.es/ActividadesColectivas/"
					f"ActividadesColectivasHorarioSemanal?fecha={date_str}"
					f"&integration=False&publico=False"
				)
				print(f"  Fetching week {week_offset + 1} ({week_date.strftime('%Y-%m-%d')})...")
				await page.goto(url)
				await page.wait_for_load_state("networkidle", timeout=30000)
				await asyncio.sleep(2)

				week_classes = await extract_classes_from_page(page)
				all_classes.extend(week_classes)
				print(f"    Found {len(week_classes)} classes")

			print(f"  Total: {len(all_classes)} classes")

			now = datetime.now(timezone.utc).replace(tzinfo=None)
			future_classes = [
				cls for cls in all_classes
				if cls.get("HoraFin") and datetime.fromisoformat(cls["HoraFin"]) >= now
			]
			print(f"  {len(future_classes)} future classes")

			filtered_classes = filter_classes(future_classes)
			print(f"  {len(filtered_classes)} classes match filters")

			output_file = "ics_files/metropolitan_classes.ics"
			event_count = classes_to_ical(filtered_classes, output_file)
			print(f"  Created {output_file} with {event_count} events")

			await browser.close()
			last_fetch_time = datetime.now()
			print(f"Fetch complete at {last_fetch_time.strftime('%Y-%m-%d %H:%M:%S')}")

	except Exception as e:
		print(f"Error fetching gym classes: {e}")
	finally:
		fetch_in_progress = False


# --- Routes ---

@app.get("/")
async def root():
	return Response(status_code=204)


@app.get("/calendar.ics")
async def get_calendar(alert: int | None = Query(default=None, description="Reminder minutes before class")):
	"""Serve the merged and filtered calendar.

	/calendar.ics          — no alerts
	/calendar.ics?alert=25 — 25 min reminder on each event
	"""
	ics_content = merge_and_filter_ics_files(reminder_minutes=alert)

	if ics_content is None:
		return PlainTextResponse(content="No calendar data available", status_code=404)

	return Response(
		content=ics_content,
		media_type="text/calendar; charset=utf-8",
		headers={
			"Content-Disposition": "inline; filename=calendar.ics",
			"Cache-Control": "no-cache",
		},
	)


@app.get("/health")
async def health_check():
	ics_files = list(ICS_DIR.glob("*.ics"))
	cookies_valid = check_cookies_valid() if scraper_available else None
	return {
		"status": "healthy",
		"ics_files_count": len(ics_files),
		"last_fetch": last_fetch_time.isoformat() if last_fetch_time else None,
		"fetch_in_progress": fetch_in_progress,
		"cookies_valid": cookies_valid,
	}


@app.post("/refresh")
async def refresh_data(background_tasks: BackgroundTasks):
	if fetch_in_progress:
		return {"status": "already_in_progress"}
	background_tasks.add_task(fetch_gym_classes_background)
	return {"status": "refresh_started"}


@app.get("/check")
async def check_connection(force_login: bool = False):
	"""Check if server can reach the gym website and fetch classes."""
	if not scraper_available or not USERNAME or not PASSWORD:
		return {"status": "error"}

	try:
		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=True)
			context = await browser.new_context()

			cookies_valid = check_cookies_valid() and not force_login
			if cookies_valid:
				from gym_calendar.scraper import load_cookies
				await context.add_cookies(load_cookies())
			else:
				from gym_calendar.scraper import login_and_save_cookies, load_cookies
				await login_and_save_cookies(context, USERNAME, PASSWORD)
				await context.add_cookies(load_cookies())

			page = await context.new_page()
			await navigate_to_gym(page)

			all_classes = []
			today = datetime.now()
			for week_offset in range(3):
				week_date = today + timedelta(weeks=week_offset)
				date_str = week_date.strftime("%Y-%m-%dT00:00:00")
				url = (
					f"https://clubmetropolitan.provis.es/ActividadesColectivas/"
					f"ActividadesColectivasHorarioSemanal?fecha={date_str}"
					f"&integration=False&publico=False"
				)
				await page.goto(url)
				await page.wait_for_load_state("networkidle", timeout=30000)
				await asyncio.sleep(1)
				week_classes = await extract_classes_from_page(page)
				all_classes.extend(week_classes)

			await browser.close()

			if not all_classes:
				return {"status": "error"}

			now = datetime.now(timezone.utc).replace(tzinfo=None)
			future_count = sum(
				1 for cls in all_classes
				if cls.get("HoraFin") and datetime.fromisoformat(cls["HoraFin"]) >= now
			)

			return {
				"status": "ok",
				"cookies_valid": cookies_valid,
				"cookies_refreshed": not cookies_valid,
				"future_classes": future_count,
			}

	except Exception:
		return {"status": "error"}


@app.on_event("startup")
async def startup_event():
	port = int(os.getenv("PORT", 8000))
	print(f"Gym Calendar Server starting on port {port}")
	print(f"  Calendar: http://localhost:{port}/calendar.ics")
	print(f"  Health:   http://localhost:{port}/health")
	print(f"  Refresh:  POST http://localhost:{port}/refresh")

	if scraper_available and USERNAME and PASSWORD:
		print("  Fetching initial data...")
		await fetch_gym_classes_background()


if __name__ == "__main__":
	import sys

	port = 3083
	for i, arg in enumerate(sys.argv[1:], 1):
		if arg.startswith("--port="):
			port = int(arg.split("=")[1])
			break
		elif arg == "--port" and i < len(sys.argv) - 1:
			port = int(sys.argv[i + 1])
			break
	else:
		if os.getenv("PORT"):
			port = int(os.getenv("PORT"))

	os.environ["PORT"] = str(port)
	uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
