CREATE TABLE paste_table (
"id" INTEGER PRIMARY KEY,
    "code" BLOB,
    "user_ip" TEXT,
    "lexer" TEXT,
    "seen_delete" INTEGER NOT NULL DEFAULT (0),
    "id_sec" TEXT
    );
