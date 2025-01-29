DROP TABLE IF EXISTS hashes;
CREATE TABLE hashes (
	id SERIAL PRIMARY KEY,
	hash bigint,
	url text,
    preview_url text,
    label text,
    filename text,
    size text,
    filesize text
);
CREATE EXTENSION bktree;
CREATE INDEX index ON hashes USING spgist (hash bktree_ops);