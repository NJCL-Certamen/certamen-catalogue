CREATE OR REPLACE TABLE tournament (
  id CHAR(16) PRIMARY KEY, -- the script will generate a UUID, but feel free to switch to your preferred form of id
  name VARCHAR(75)
);

CREATE OR REPLACE TABLE round (
  id CHAR(16) PRIMARY KEY,
  round VARCHAR(15), -- Round 1, Round 2, etc.
  tournament_id CHAR(16),
  FOREIGN_KEY tournament_id REFERENCES tournament(id)
);

CREATE OR REPLACE TABLE tossup (
  id CHAR(16) PRIMARY KEY,
  question NVARCHAR(600) -- this is extra big for passages, if you don't want to search by the text in this field, you might consider moving to a binary data type instead
  answer NVARCHAR(300) -- NVARCHAR type is an engine agnostic means of supporting long vowels and diareses, other engine specific solutions exist like CHARACTER SET utf8mb4 for MySQL
  round_id CHAR(16),
  question_number TINYINT,
  FOREIGN_KEY round_id REFERENCES round(id)
);

CREATE OR REPLACE TABLE bonus (
  tossup_id CHAR(16),
  bonus_number TINYINT,
  question NVARCHAR(600),
  answer NVARCHAR(300),
  PRIMARY KEY (tossup_id, bonus_number), -- going with a compound key on the assumption that boni won't need to be looked up on their own without reference to the tossup that much
  FOREIGN KEY tossup_id REFERENCES tossup(id)
);
