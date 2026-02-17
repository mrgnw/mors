use anyhow::Result;
use chrono::{Duration, NaiveDateTime, Utc};
use icalendar::{parser, Alarm, Calendar, Component, Event, EventLike};
use std::collections::HashSet;
use std::fs;
use std::path::Path;

use crate::config;

pub fn merge_and_filter(ics_dir: &Path, alert_minutes: Option<i64>) -> Result<Option<String>> {
	merge_and_filter_classes(ics_dir, alert_minutes, None)
}

pub fn merge_and_filter_classes(
	ics_dir: &Path,
	alert_minutes: Option<i64>,
	class_filters: Option<&[&str]>,
) -> Result<Option<String>> {
	if !ics_dir.exists() {
		return Ok(None);
	}

	let ics_files: Vec<_> = fs::read_dir(ics_dir)?
		.filter_map(|e| e.ok())
		.filter(|e| e.path().extension().is_some_and(|ext| ext == "ics"))
		.collect();

	if ics_files.is_empty() {
		return Ok(None);
	}

	tracing::info!("Found {} .ics file(s)", ics_files.len());

	let today = Utc::now().naive_utc().date();
	let mut merged = Calendar::new();
	merged.name("Gym Classes");
	merged.append_property(("X-WR-TIMEZONE", "Europe/Madrid"));

	let mut seen_uids: HashSet<String> = HashSet::new();
	let mut event_count = 0u32;

	for entry in &ics_files {
		let content = match fs::read_to_string(entry.path()) {
			Ok(c) => c,
			Err(e) => {
				tracing::warn!("Error reading {}: {}", entry.path().display(), e);
				continue;
			}
		};

		let unfolded = parser::unfold(&content);
		let parsed = match parser::read_calendar(&unfolded) {
			Ok(cal) => cal,
			Err(e) => {
				tracing::warn!("Error parsing {}: {}", entry.path().display(), e);
				continue;
			}
		};

		for component in &parsed.components {
			if component.name.as_str() != "VEVENT" {
				continue;
			}

			let uid = component
				.find_prop("UID")
				.and_then(|p| Some(p.val.as_str().to_string()));

			if let Some(ref uid) = uid {
				if seen_uids.contains(uid) {
					continue;
				}
				seen_uids.insert(uid.clone());
			}

			let dtstart = component
				.find_prop("DTSTART")
				.map(|p| p.val.as_str());

			if let Some(dt_str) = dtstart {
				if let Some(dt) = parse_ical_datetime(dt_str) {
					if dt.date() < today {
						continue;
					}
				}
			}

			if let Some(filters) = class_filters {
				let summary = component
					.find_prop("SUMMARY")
					.map(|p| p.val.as_str())
					.unwrap_or("");
				let summary_lower = summary.to_lowercase();
				let matches = filters
					.iter()
					.any(|f| summary_lower.contains(&f.to_lowercase()));
				if !matches {
					continue;
				}
			}

			let mut event = Event::new();
			for prop in &component.properties {
				let name = prop.name.as_str();
				let val = prop.val.as_str();
				match name {
					"UID" => { event.uid(val); }
					"SUMMARY" => { event.summary(val); }
					"DESCRIPTION" => { event.description(val); }
					"LOCATION" => { event.location(val); }
					"DTSTART" | "DTEND" | "DTSTAMP" => {
						event.append_property((name, val));
					}
					_ => {
						event.append_property((name, val));
					}
				}
			}

			if let Some(minutes) = alert_minutes {
				let summary = component
					.find_prop("SUMMARY")
					.map(|p| p.val.as_str())
					.unwrap_or("Class");
				event.alarm(Alarm::display(
					&format!("{summary} starts in {minutes} minutes"),
					-Duration::minutes(minutes),
				));
			}

			merged.push(event.done());
			event_count += 1;
		}
	}

	if event_count == 0 {
		return Ok(None);
	}

	tracing::info!("{event_count} future events");
	Ok(Some(merged.to_string()))
}

fn parse_ical_datetime(s: &str) -> Option<NaiveDateTime> {
	let s = s.trim_end_matches('Z');
	NaiveDateTime::parse_from_str(s, "%Y%m%dT%H%M%S").ok()
}

pub fn display_name(raw: &str) -> String {
	config::display_name(raw)
}
