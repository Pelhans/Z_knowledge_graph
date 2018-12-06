CREATE TABLE lemmas( title VARCHAR(100), title_id INT NOT NULL, abstract TEXT, infobox TEXT, subject VARCHAR(100), disambi VARCHAR(100), interPic TEXT, interLink TEXT, exterLink TEXT, relateLemma TEXT, all_text TEXT, PRIMARY KEY(title_id), unique KEY(disambi) USING HASH );

ALTER TABLE lemmas CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
