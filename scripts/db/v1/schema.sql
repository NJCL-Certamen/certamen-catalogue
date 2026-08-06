CREATE TABLE tournament (
  id CHAR(32) PRIMARY KEY, -- the script will generate a UUID, but feel free to switch to your preferred form of id
  tournament_name VARCHAR(75) UNIQUE
);

CREATE TABLE round (
  id CHAR(32) PRIMARY KEY,
  round VARCHAR(15), -- Round 1, Round 2, etc.
  year CHAR(4),
  tournament_id CHAR(32) REFERENCES tournament(id)
);

CREATE TABLE tossup (
  id CHAR(32) PRIMARY KEY,
  question NVARCHAR(600), -- this is extra big for passages, if you don't want to search by the text in this field, you might consider moving to a binary data type instead
  answer NVARCHAR(300), -- NVARCHAR type is an engine agnostic means of supporting long vowels and diareses, other engine specific solutions exist like CHARACTER SET utf8mb4 for MySQL
  round_id CHAR(32) REFERENCES round(id),
  question_number TINYINT
);

CREATE TABLE bonus (
  tossup_id CHAR(32) REFERENCES tossup(id),
  bonus_number TINYINT,
  question NVARCHAR(600),
  answer NVARCHAR(300),
  PRIMARY KEY (tossup_id, bonus_number) -- going with a compound key on the assumption that boni won't need to be looked up on their own without reference to the tossup that much
);
