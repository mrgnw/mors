from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from icalendar import Calendar, Event

from .config import CLASS_DISPLAY_NAMES, DEFAULT_CLASS_FILTERS, GYM_ADDRESS


def display_name(raw_name):
	"""Map a raw ALL-CAPS class name to emoji + title-cased display name."""
	return CLASS_DISPLAY_NAMES.get(raw_name, raw_name.title())


def filter_classes(classes, name_filters=None):
	"""Filter classes whose Nombre matches any of the filter strings."""
	if not name_filters:
		name_filters = DEFAULT_CLASS_FILTERS
	if not name_filters:
		return classes

	needles = [f.lower() for f in name_filters]
	filtered = []
	for cls in classes:
		name = cls.get("Nombre", "").lower()
		if not name:
			continue
		if any(needle in name for needle in needles):
			filtered.append(cls)
	return filtered


def classes_to_ical(classes, output_file):
	"""Convert class dicts to an .ics file (no alarms)."""
	cal = Calendar()
	cal.add('prodid', '-//Metropolitan Gym Classes//EN')
	cal.add('version', '2.0')
	cal.add('method', 'PUBLISH')
	cal.add('calscale', 'GREGORIAN')
	cal.add('x-wr-calname', 'Gym Classes')
	cal.add('x-wr-timezone', 'Europe/Madrid')

	MADRID = ZoneInfo("Europe/Madrid")
	now_utc = datetime.now(timezone.utc)
	now = now_utc.replace(tzinfo=None)
	event_count = 0
	seen_ids = set()

	for cls in classes:
		class_id = cls.get('Id', 0)
		if class_id in seen_ids:
			continue
		seen_ids.add(class_id)

		try:
			start_str = cls.get("HoraInicio")
			end_str = cls.get("HoraFin")
			if not start_str or not end_str:
				continue

			start_dt = datetime.fromisoformat(start_str)
			end_dt = datetime.fromisoformat(end_str)
			if end_dt < now:
				continue

			event = Event()
			event.add('uid', f"{class_id}@metropolitan.provis.es")
			event.add('dtstamp', now_utc)
			event.add('dtstart', start_dt.replace(tzinfo=MADRID))
			event.add('dtend', end_dt.replace(tzinfo=MADRID))
			event.add('last-modified', now_utc)
			event.add('sequence', 0)
			event.add('class', 'PUBLIC')
			event.add('transp', 'TRANSPARENT')

			summary = display_name(cls.get("Nombre", "Class"))
			event.add('summary', summary)

			description_parts = []
			if cls.get("NombreTrabajador"):
				instructor = f"{cls['NombreTrabajador']} {cls.get('ApellidosTrabajador', '')}".strip()
				description_parts.append(f"Instructor: {instructor}")
			if cls.get("nombreZona"):
				description_parts.append(f"Room: {cls['nombreZona'].strip()}")
			if cls.get("NombreAgrupacion"):
				description_parts.append(f"Category: {cls['NombreAgrupacion']}")

			capacity = cls.get("Capacidad", 0)
			reservas = cls.get("ReservasHechas", 0)
			description_parts.append(f"Availability: {capacity - reservas}/{capacity} spots")

			if cls.get("EstaReservadaPorLaPersona"):
				description_parts.append("You have reserved this class")

			event.add('description', "\n".join(description_parts))
			event.add('location', GYM_ADDRESS)
			cal.add_component(event)
			event_count += 1

		except Exception as e:
			print(f"  Warning: Skipping class {cls.get('Nombre')}: {e}")
			continue

	output_path = Path(output_file)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with open(output_file, 'wb') as f:
		f.write(cal.to_ical())

	return event_count
