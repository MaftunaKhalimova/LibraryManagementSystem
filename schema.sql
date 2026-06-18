-- Library Management System — Database Schema
-- Run this script to create all required tables from scratch.

CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title   TEXT    NOT NULL,
    author  TEXT    NOT NULL,
    isbn    TEXT    UNIQUE NOT NULL,
    status  TEXT    NOT NULL DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    email     TEXT    UNIQUE NOT NULL,
    join_date TEXT    NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS borrowing_records (
    record_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL,
    member_id   INTEGER NOT NULL,
    issue_date  TEXT    NOT NULL DEFAULT CURRENT_DATE,
    return_date TEXT,
    FOREIGN KEY (book_id)   REFERENCES books   (book_id),
    FOREIGN KEY (member_id) REFERENCES members (member_id)
);
