use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::LazyLock;

pub fn port() -> u16 {
	std::env::var("PORT")
		.ok()
		.and_then(|p| p.parse().ok())
		.unwrap_or(3083)
}

pub fn ics_dir() -> PathBuf {
	PathBuf::from(
		std::env::var("ICS_DIR").unwrap_or_else(|_| "../ics_files".into()),
	)
}

pub static CLASS_DISPLAY_NAMES: LazyLock<HashMap<&str, &str>> = LazyLock::new(|| {
	HashMap::from([
		("BODY PUMP", "🏋️ Body Pump"),
		("YOGA", "🧘 Yoga"),
		("ZUMBA", "🪩 Zumba"),
		("GAP", "🍑 GAP"),
		("PILATES-STRETCH", "🌀 Pilates Stretch"),
		("PILATES-STRONG", "💪 Pilates Strong"),
		("FITNESS CONDITION", "🔥 Fitness Condition"),
		("SUSPENSION TRAINING", "⚡ Suspension Training"),
		("SKILL RUNNING", "🏃 Skill Running"),
		("ESPALDA SANA", "🦴 Espalda Sana"),
		("BODY BALANCE", "☯️ Body Balance"),
		("BODY COMBAT", "🥊 Body Combat"),
		("CYCLING", "🚴 Cycling"),
		("CYCLING VIRTUAL", "🚴 Cycling Virtual"),
		("STRETCHING", "🙆 Stretching"),
		("ABDOMINALES", "💎 Abdominales"),
		("CROSS-HIIT CHALLENGE", "💥 Cross-HIIT Challenge"),
		("CROSS-HIIT FULL BODY", "💥 Cross-HIIT Full Body"),
		("CROSS-HIIT LOWER BODY", "💥 Cross-HIIT Lower Body"),
		("CROSS-HIIT UPPER BODY", "💥 Cross-HIIT Upper Body"),
		("CROSS-MET", "💥 Cross-Met"),
		("AQUAGYM", "🏊 Aquagym"),
		("AQUAGYM-30", "🏊 Aquagym 30"),
		("MIO-STRETCH", "🧘 Mio-Stretch"),
		("RUNNING CLUB", "🏃 Running Club"),
	])
});

pub static DEFAULT_CLASS_FILTERS: &[&str] = &[
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
];

pub fn display_name(raw: &str) -> String {
	CLASS_DISPLAY_NAMES
		.get(raw)
		.map(|s| s.to_string())
		.unwrap_or_else(|| {
			raw.split_whitespace()
				.map(|w| {
					let mut chars = w.chars();
					match chars.next() {
						Some(c) => {
							c.to_uppercase().to_string() + &chars.as_str().to_lowercase()
						}
						None => String::new(),
					}
				})
				.collect::<Vec<_>>()
				.join(" ")
		})
}
