use chrono::{DateTime, Utc};
use std::sync::{Arc, Mutex};

#[derive(Clone)]
pub struct AppState {
	pub inner: Arc<Inner>,
}

pub struct Inner {
	pub started_at: DateTime<Utc>,
	pub last_fetch: Mutex<Option<DateTime<Utc>>>,
	pub fetch_in_progress: Mutex<bool>,
}

impl AppState {
	pub fn new() -> Self {
		Self {
			inner: Arc::new(Inner {
				started_at: Utc::now(),
				last_fetch: Mutex::new(None),
				fetch_in_progress: Mutex::new(false),
			}),
		}
	}
}
