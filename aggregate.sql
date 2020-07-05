SELECT DISTINCT
  "table".id AS acousticId,
   mbid AS musicbrainzId,
   "table".fingerprint AS fingerprint
FROM mbid
INNER JOIN fpmbid, "table" ON
  fpmbid.track_id = mbid.track_id AND
  "table".id = fpmbid.fingerprint_id;
