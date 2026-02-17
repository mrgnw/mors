mod config;
mod ical;
mod routes;
mod state;

use axum::{routing::get, Router};
use state::AppState;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
	dotenvy::from_filename("../.env").ok();

	tracing_subscriber::fmt::init();

	let port = config::port();
	let state = AppState::new();

	let app = Router::new()
		.route("/", get(routes::dashboard::index))
		.route("/calendar.ics", get(routes::calendar::get_calendar))
		.route("/health", get(routes::health::health_check))
		.route("/refresh", axum::routing::post(routes::refresh::refresh))
		.with_state(state);

	let addr = format!("0.0.0.0:{port}");
	tracing::info!("Listening on {addr}");
	tracing::info!("  Calendar: http://localhost:{port}/calendar.ics");
	tracing::info!("  Health:   http://localhost:{port}/health");

	let listener = tokio::net::TcpListener::bind(&addr).await?;
	axum::serve(listener, app).await?;

	Ok(())
}
