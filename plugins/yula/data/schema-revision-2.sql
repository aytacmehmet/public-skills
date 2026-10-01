-- Additive revision: base SQLite/reader ABI remains user_version=1.
CREATE INDEX IF NOT EXISTS objects_exact_name ON objects(object_name COLLATE NOCASE,object_type);
CREATE INDEX IF NOT EXISTS catalog_exact_name ON released_catalog(edition,object_name COLLATE NOCASE,object_type);
CREATE UNIQUE INDEX IF NOT EXISTS cfg_change_identity ON cfg_changes(release,entry_id);
CREATE UNIQUE INDEX IF NOT EXISTS cfg_dependency_identity ON cfg_dependencies(release,edge_id);
CREATE UNIQUE INDEX IF NOT EXISTS cfg_lesson_identity ON cfg_lessons(release,lesson_id);
CREATE UNIQUE INDEX IF NOT EXISTS cfg_incident_identity ON cfg_incidents(release,incident_id);
CREATE TABLE IF NOT EXISTS doc_topic_evidence (
    document_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    source_id TEXT,
    fetched_at TEXT,
    build TEXT,
    joiner TEXT NOT NULL,
    representation TEXT NOT NULL CHECK(representation IN ('source_text','legacy_chunks')),
    text_sha256 TEXT NOT NULL CHECK(length(text_sha256)=64),
    PRIMARY KEY(document_id,topic_id),
    FOREIGN KEY(document_id) REFERENCES doc_documents(document_id) ON DELETE CASCADE,
    FOREIGN KEY(source_id) REFERENCES yula_sources(id) DEFERRABLE INITIALLY DEFERRED
);
