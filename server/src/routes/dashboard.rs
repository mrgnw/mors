use axum::http::StatusCode;
use axum::response::IntoResponse;

pub async fn index() -> impl IntoResponse {
	StatusCode::NO_CONTENT
}
