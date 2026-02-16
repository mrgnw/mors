import asyncio
import json
from datetime import datetime

from .config import COOKIES_FILE


def check_cookies_valid():
	"""Check if saved cookies exist and metropolitan_token is not expired."""
	if not COOKIES_FILE.exists():
		return False
	try:
		cookies = json.loads(COOKIES_FILE.read_text())
		for cookie in cookies:
			if cookie['name'] == 'metropolitan_token':
				expires = cookie.get('expires')
				if expires and expires > datetime.now().timestamp():
					return True
	except Exception:
		pass
	return False


def load_cookies():
	"""Load cookies from disk."""
	return json.loads(COOKIES_FILE.read_text())


def save_cookies(cookies):
	"""Save cookies to disk."""
	COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
	COOKIES_FILE.write_text(json.dumps(cookies, indent=2))


async def login_and_save_cookies(context, username, password):
	"""Login to Metropolitan and save cookies."""
	page = await context.new_page()

	print("  Logging in...")
	await page.goto("https://clubmetropolitan.com/socios/login")
	await page.wait_for_selector('input[name="email"]', timeout=15000)

	await page.fill('input[name="email"]', username)
	await page.fill('input[name="pwd"]', password)
	await page.press('input[name="pwd"]', 'Enter')

	await page.wait_for_load_state("networkidle", timeout=30000)

	cookies = await context.cookies()
	save_cookies(cookies)
	print("  Logged in and saved cookies")
	await page.close()


async def ensure_authenticated(context, username, password):
	"""Load cached cookies or login. Returns nothing, sets cookies on context."""
	if check_cookies_valid():
		print("  Using cached cookies")
		await context.add_cookies(load_cookies())
	else:
		print("  No valid cookies, logging in...")
		await login_and_save_cookies(context, username, password)
		await context.add_cookies(load_cookies())


async def navigate_to_gym(page):
	"""Navigate to Sagrada Familia schedule page, return the page."""
	print("  Setting location to Sagrada Familia...")
	await page.goto(
		"https://clubmetropolitan.provis.es/Layout/CambiarInstalacion"
		"?idmultiinstalacion=823"
		"&returnUrl=/ActividadesColectivas/ActividadesColectivasHorarioSemanal"
	)
	await page.wait_for_load_state("networkidle", timeout=30000)
	await asyncio.sleep(3)

	location_name = await page.evaluate("() => document.querySelector('h1')?.textContent.trim()")
	if location_name and "SAGRADA FAMILIA" in location_name.upper():
		print(f"  Confirmed location: {location_name}")
	else:
		print(f"  Warning: Location shows as '{location_name}' (expected Sagrada Familia)")


EXTRACT_JS = """
() => {
	const nodes = Array.from(document.querySelectorAll('[data-json]'));

	const NAME_KEYS = ["Nombre", "nombreActividad", "summary", "title", "name"];
	const FIELD_MAP = {
		start: ["HoraInicio", "fechaInicio", "start", "startDate", "startTime"],
		end: ["HoraFin", "fechaFin", "end", "endDate", "endTime"],
	};

	function collect(node, target) {
		if (!node) return;
		if (Array.isArray(node)) {
			for (const entry of node) collect(entry, target);
			return;
		}
		if (typeof node !== 'object') return;

		const hasName = NAME_KEYS.some(key => key in node);
		const hasStart = FIELD_MAP.start.some(key => key in node);
		const hasEnd = FIELD_MAP.end.some(key => key in node);

		if (hasName && (hasStart || hasEnd)) {
			target.push(node);
			return;
		}
		for (const value of Object.values(node)) {
			collect(value, target);
		}
	}

	const seen = new Set();
	const results = [];

	for (const el of nodes) {
		const raw = el.getAttribute('data-json');
		if (!raw || seen.has(raw)) continue;
		seen.add(raw);
		try {
			collect(JSON.parse(raw), results);
		} catch (err) {}
	}

	return results;
}
"""


async def extract_classes_from_page(page):
	"""Extract class data from [data-json] attributes on the current page."""
	return await page.evaluate(EXTRACT_JS)
