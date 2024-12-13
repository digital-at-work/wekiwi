CREATE TABLE artists(
    id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE albums(
    id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR NOT NULL,
    artist_id INT,
    PRIMARY KEY(id),
    CONSTRAINT fk_artist
      FOREIGN KEY(artist_id)
        REFERENCES artists(id)
          ON DELETE CASCADE
);

CREATE INDEX fk_albums_artist_id ON albums(artist_id);
