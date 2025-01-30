DROP TABLE IF EXISTS hashes;
CREATE TABLE hashes (
	id SERIAL PRIMARY KEY,
	hash bigint,
	url text,
    preview_url text,
    label text,
    filename text,
    size text,
    filesize text,
    camera_name text, 
    aperture text, 
    exposure text, 
    focal_length text, 
    location text, 
    location_name text
);
CREATE EXTENSION bktree;
CREATE INDEX index ON hashes USING spgist (hash bktree_ops);