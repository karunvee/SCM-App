
SQLITE MANAGEMENT
$ python manage.py dbshell

> (Inside the DB shell)
> DROP TABLE {app-name}_{model-name};

PRAGMA foreign_keys = ON;  -- Enable foreign key support in SQLite

CREATE TABLE main_inventoryreport (
    id TEXT PRIMARY KEY,  -- Store UUIDs as text
    component_id TEXT NOT NULL,
    status TEXT CHECK (status IN ('Abnormal', 'Normal')) DEFAULT 'Abnormal',
    inventory_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (component_id) REFERENCES Component(id) ON DELETE CASCADE
);
