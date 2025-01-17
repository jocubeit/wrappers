#![allow(clippy::module_inception)]
mod airtable_fdw;
mod result;

use pgrx::pg_sys::panic::ErrorReport;
use pgrx::prelude::PgSqlErrorCode;
use thiserror::Error;

use supabase_wrappers::prelude::{CreateRuntimeError, OptionsError};

#[derive(Error, Debug)]
enum AirtableFdwError {
    #[error("column '{0}' data type is not supported")]
    UnsupportedColumnType(String),

    #[error("column '{0}' data type not match")]
    ColumnTypeNotMatch(String),

    #[error("{0}")]
    CreateRuntimeError(#[from] CreateRuntimeError),

    #[error("parse url failed: {0}")]
    UrlParseError(#[from] url::ParseError),

    #[error("request failed: {0}")]
    RequestError(#[from] reqwest_middleware::Error),

    #[error("{0}")]
    OptionsError(#[from] OptionsError),
}

impl From<AirtableFdwError> for ErrorReport {
    fn from(value: AirtableFdwError) -> Self {
        match value {
            AirtableFdwError::CreateRuntimeError(e) => e.into(),
            AirtableFdwError::OptionsError(e) => e.into(),
            _ => ErrorReport::new(PgSqlErrorCode::ERRCODE_FDW_ERROR, format!("{value}"), ""),
        }
    }
}

type AirtableFdwResult<T> = Result<T, AirtableFdwError>;
