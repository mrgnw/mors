use axum::extract::{Path, Query};
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
		Ok(Some(content)) => ical_response(content, "calendar.ics"),
		Ok(None) => (StatusCode::NOT_FOUND, "No calendar data available").into_response(),
		Err(e) => {
			tracing::error!("Error merging calendars: {e}");
			(StatusCode::INTERNAL_SERVER_ERROR, "Internal error").into_response()
		}
	}
}

pub async fn get_filtered_calendar(
	Path(slug): Path<String>,
	Query(params): Query<CalendarParams>,
) -> impl IntoResponse {
	let slug = slug.trim_end_matches(".ics");

	if slug == "all" {
		let ics_dir = config::ics_dir();
		return match ical::merge_and_filter_classes(&ics_dir, params.alert, None) {
			Ok(Some(content)) => ical_response(content, "all.ics"),
			Ok(None) => (StatusCode::NOT_FOUND, "No calendar data available").into_response(),
			Err(e) => {
				tracing::error!("Error merging calendars: {e}");
				(StatusCode::INTERNAL_SERVER_ERROR, "Internal error").into_response()
			}
		};
	}

	let filters = match config::slug_filters(slug) {
		Some(f) => f,
		None => {
			let available: Vec<&str> = config::CALENDAR_SLUGS.keys().copied().collect();
			let msg = format!("Unknown class: {slug}. Available: {}, all", available.join(", "));
			return (StatusCode::NOT_FOUND, msg).into_response();
		}
	};

	let ics_dir = config::ics_dir();
	match ical::merge_and_filter_classes(&ics_dir, params.alert, Some(filters)) {
		Ok(Some(content)) => ical_response(content, &format!("{slug}.ics")),
		Ok(None) => (StatusCode::NOT_FOUND, format!("No events for '{slug}'")).into_response(),
		Err(e) => {
			tracing::error!("Error merging calendars: {e}");
			(StatusCode::INTERNAL_SERVER_ERROR, "Internal error").into_response()
		}
	}
}

fn ical_response(content: String, filename: &str) -> axum::response::Response {
	let mut headers = HeaderMap::new();
	headers.insert(
		"content-type",
		"text/calendar; charset=utf-8".parse().unwrap(),
	);
	headers.insert(
		"content-disposition",
		format!("inline; filename={filename}").parse().unwrap(),
	);
	headers.insert("cache-control", "no-cache".parse().unwrap());
	(StatusCode::OK, headers, content).into_response()
}
