CREATE TABLE cfg_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE cfg_activities (
                release TEXT NOT NULL, source_row INTEGER NOT NULL, activity_id TEXT,
                activity_name TEXT, application_area TEXT, application_subarea TEXT,
                configuration_item_id TEXT, configuration_item_name TEXT, category TEXT,
                scope_item_id TEXT, scope_item_description TEXT, locality_type TEXT,
                specialized_countries TEXT, img_activity TEXT, component_id TEXT,
                configuration_approach TEXT, redo_in_p TEXT, delete_customer_records TEXT,
                file_upload_enabled TEXT, is_expert INTEGER, json TEXT NOT NULL,
                PRIMARY KEY (release, source_row)
            );
CREATE TABLE cfg_access_map (
                release TEXT, source_row INTEGER, business_catalog_id TEXT, description TEXT,
                transaction_code TEXT, iam_app_id TEXT, img_activity TEXT, sscui_id TEXT,
                component_id TEXT, json TEXT NOT NULL
            );
CREATE TABLE cfg_expert_config (release TEXT, activity_id TEXT, title TEXT, json TEXT NOT NULL);
CREATE TABLE cfg_changes (release TEXT, entry_id TEXT, title TEXT, change_type TEXT,
                                  activity_ids TEXT, valid_from TEXT, source_url TEXT, json TEXT NOT NULL);
CREATE TABLE cfg_dependencies (release TEXT, edge_id TEXT, source_activity_id TEXT,
                                       target_activity_id TEXT, relation TEXT, status TEXT,
                                       evidence_level TEXT, json TEXT NOT NULL);
CREATE TABLE cfg_incidents (release TEXT, incident_id TEXT, status TEXT,
                                    related_activity_ids TEXT, created_at TEXT, json TEXT NOT NULL);
CREATE TABLE cfg_lessons (release TEXT, lesson_id TEXT, status TEXT,
                                  activity_ids TEXT, confidence_score INTEGER, json TEXT NOT NULL);
CREATE TABLE cfg_documents (
                doc_id TEXT PRIMARY KEY, release TEXT, doc_type TEXT, entity_id TEXT,
                section TEXT, title TEXT, body TEXT, tags TEXT, source_path TEXT,
                updated_at TEXT, json TEXT NOT NULL
            );
CREATE VIRTUAL TABLE cfg_documents_fts USING fts5(
                doc_id UNINDEXED, release UNINDEXED, doc_type UNINDEXED,
                entity_id UNINDEXED, section UNINDEXED,
                title, body, tags,
                tokenize='unicode61 remove_diacritics 2'
            );
CREATE TABLE doc_documents (
                document_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                root_url TEXT NOT NULL,
                scope TEXT NOT NULL,
                version TEXT NOT NULL,
                language TEXT NOT NULL,
                topics INTEGER NOT NULL
            );
CREATE VIRTUAL TABLE doc_chunks USING fts5(
                chunk_id UNINDEXED,
                document_id UNINDEXED,
                document_title,
                topic_id UNINDEXED,
                topic_title,
                breadcrumb,
                url UNINDEXED,
                root_url UNINDEXED,
                scope UNINDEXED,
                text,
                tokenize='unicode61 remove_diacritics 2'
            );

CREATE TABLE cfg_profiles(release TEXT NOT NULL,activity_id TEXT NOT NULL,json TEXT NOT NULL,PRIMARY KEY(release,activity_id));
CREATE TABLE cfg_sources(release TEXT NOT NULL,activity_id TEXT NOT NULL,source_id TEXT NOT NULL,json TEXT NOT NULL,PRIMARY KEY(release,activity_id,source_id));
CREATE TABLE yula_sources(id TEXT PRIMARY KEY,kind TEXT NOT NULL,fingerprint TEXT NOT NULL,fetched_at TEXT,verified_at TEXT NOT NULL,details_json TEXT NOT NULL);
CREATE TABLE yula_aliases(term TEXT PRIMARY KEY,expansion TEXT NOT NULL);
CREATE TABLE yula_records(kind TEXT,id TEXT,release TEXT,revision INTEGER,sha256 TEXT,recorded_at TEXT,json TEXT,PRIMARY KEY(kind,id,release,revision));
CREATE TABLE yula_review_flags(release TEXT,activity_id TEXT,reason TEXT,flagged_at TEXT,PRIMARY KEY(release,activity_id,reason));
CREATE TABLE yula_observations(source_id TEXT,object_type TEXT,object_name TEXT,sha256 TEXT,observed_at TEXT,json TEXT,PRIMARY KEY(source_id,object_type,object_name));
CREATE TABLE yula_migrations(version INTEGER PRIMARY KEY,applied_at TEXT,description TEXT);
CREATE INDEX cfg_activity_id ON cfg_activities(release,activity_id);
CREATE INDEX cfg_access_sscui ON cfg_access_map(release,sscui_id);
CREATE INDEX cfg_access_img ON cfg_access_map(release,img_activity);
CREATE INDEX cfg_doc_entity ON cfg_documents(release,entity_id,doc_type);
