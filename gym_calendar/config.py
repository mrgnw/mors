from pathlib import Path

GYM_ADDRESS = "Metropolitan Sagrada Familia\nCalle Provença, 408"

CLASS_DISPLAY_NAMES = {
	"BODY PUMP": "🏋️ Body Pump",
	"YOGA": "🧘 Yoga",
	"ZUMBA": "🪩 Zumba",
	"GAP": "🍑 GAP",
	"PILATES-STRETCH": "🌀 Pilates Stretch",
	"PILATES-STRONG": "💪 Pilates Strong",
	"FITNESS CONDITION": "🔥 Fitness Condition",
	"SUSPENSION TRAINING": "⚡ Suspension Training",
	"SKILL RUNNING": "🏃 Skill Running",
	"ESPALDA SANA": "🦴 Espalda Sana",
	"BODY BALANCE": "☯️ Body Balance",
	"BODY COMBAT": "🥊 Body Combat",
	"CYCLING": "🚴 Cycling",
	"CYCLING VIRTUAL": "🚴 Cycling Virtual",
	"STRETCHING": "🙆 Stretching",
	"ABDOMINALES": "💎 Abdominales",
	"CROSS-HIIT CHALLENGE": "💥 Cross-HIIT Challenge",
	"CROSS-HIIT FULL BODY": "💥 Cross-HIIT Full Body",
	"CROSS-HIIT LOWER BODY": "💥 Cross-HIIT Lower Body",
	"CROSS-HIIT UPPER BODY": "💥 Cross-HIIT Upper Body",
	"CROSS-MET": "💥 Cross-Met",
	"AQUAGYM": "🏊 Aquagym",
	"AQUAGYM-30": "🏊 Aquagym 30",
	"MIO-STRETCH": "🧘 Mio-Stretch",
	"RUNNING CLUB": "🏃 Running Club",
}

DEFAULT_CLASS_FILTERS = [
	"body pump",
	"cross-",
	"fitness condition",
	"gap",
	"yoga",
	"zumba",
	"pilates",
	"suspension training",
	"skill running",
	"espalda sana",
]

COOKIES_FILE = Path(__file__).parent.parent / "data" / "metropolitan_cookies.json"
ICS_DIR = Path(__file__).parent.parent / "ics_files"
CONSOLIDATED_FILE = "consolidated.ics"
