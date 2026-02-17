use axum::extract::State;
use axum::Json;
use serde_json::{json, Value};
use std::fs;

use crate::config;
use crate::state::AppState;

pub async fn health_check(State(state): State<AppState>) -> Json<Value> {
	let ics_dir = config::ics_dir();
	let ics_count = fs::read_dir(&ics_dir)
		.map(|entries| {
			entries
				.filter_map(|e| e.ok())
				.filter(|e| e.path().extension().is_some_and(|ext| ext == "ics"))
				.count()
		})
		.unwrap_or(0);

	let last_fetch = state.inner.last_fetch.lock().unwrap().map(|t| t.to_rfc3339());
	let fetch_in_progress = *state.inner.fetch_in_progress.lock().unwrap();

	Json(json!({
		"status": "healthy",
		"ics_files_count": ics_count,
		"last_fetch": last_fetch,
		"fetch_in_progress": fetch_in_progress,
	}))
}
