use axum::extract::State;
use axum::Json;
use serde_json::{json, Value};
use tokio::process::Command;

use crate::state::AppState;

pub async fn refresh(State(state): State<AppState>) -> Json<Value> {
	{
		let in_progress = *state.inner.fetch_in_progress.lock().unwrap();
		if in_progress {
			return Json(json!({ "status": "already_in_progress" }));
		}
		*state.inner.fetch_in_progress.lock().unwrap() = true;
	}

	let state_clone = state.clone();
	tokio::spawn(async move {
		tracing::info!("Starting gym data refresh...");
		let uv = std::env::var("UV_PATH")
			.unwrap_or_else(|_| format!("{}/.local/bin/uv", std::env::var("HOME").unwrap_or_default()));
		let result = Command::new(&uv)
			.args(["run", "python", "fetch_gym_data.py"])
			.current_dir("..")
			.output()
			.await;

		match result {
			Ok(output) => {
				let stdout = String::from_utf8_lossy(&output.stdout);
				let stderr = String::from_utf8_lossy(&output.stderr);
				if output.status.success() {
					tracing::info!("Refresh complete:\n{stdout}");
				} else {
					tracing::error!("Refresh failed (exit {}):\n{stdout}\n{stderr}", output.status);
				}
			}
			Err(e) => {
				tracing::error!("Failed to spawn refresh: {e}");
			}
		}

		*state_clone.inner.fetch_in_progress.lock().unwrap() = false;
		*state_clone.inner.last_fetch.lock().unwrap() = Some(chrono::Utc::now());
	});

	Json(json!({ "status": "refresh_started" }))
}
