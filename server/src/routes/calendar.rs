use axum::extract::Query;
use axum::http::{HeaderMap, StatusCode};
use axum::response::IntoResponse;
use serde::Deserialize;

use crate::config;
use crate::ical;

#[derive(Deserialize)]
pub struct CalendarParams {
	pub alert: Option<i64>,
}

pub async fn get_calendar(Query(params): Query<CalendarParams>) -> impl IntoResponse {
	let ics_dir = config::ics_dir();
	match ical::merge_and_filter(&ics_dir, params.alert) {
		Ok(Some(content)) => {
			let mut headers = HeaderMap::new();
			headers.insert(
				"content-type",
				"text/calendar; charset=utf-8".parse().unwrap(),
			);
			headers.insert(
				"content-disposition",
				"inline; filename=calendar.ics".parse().unwrap(),
			);
			headers.insert("cache-control", "no-cache".parse().unwrap());
			(StatusCode::OK, headers, content).into_response()
		}
		Ok(None) => (StatusCode::NOT_FOUND, "No calendar data available").into_response(),
		Err(e) => {
			tracing::error!("Error merging calendars: {e}");
			(StatusCode::INTERNAL_SERVER_ERROR, "Internal error").into_response()
		}
	}
}
