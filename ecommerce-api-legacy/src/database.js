const { promisify } = require("util");
const sqlite3 = require("sqlite3");
const { hashPassword } = require("./lib/crypto");

function wrap(db) {
    return {
        raw: db,
        get: promisify(db.get.bind(db)),
        all: promisify(db.all.bind(db)),
        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                db.run(sql, params, function onRun(err) {
                    if (err) {
                        reject(err);
                        return;
                    }
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        },
        exec: promisify(db.exec.bind(db)),
    };
}

async function createDatabase() {
    const db = wrap(new sqlite3.Database(":memory:"));
    await db.exec(`
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            pass TEXT
        );
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY,
            title TEXT,
            price REAL,
            active INTEGER
        );
        CREATE TABLE enrollments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            course_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY,
            enrollment_id INTEGER,
            amount REAL,
            status TEXT,
            FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
        );
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY,
            action TEXT,
            created_at DATETIME
        );
    `);

    const hashed = await hashPassword("123");
    await db.run(
        "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
        ["Leonan", "leonan@fullcycle.com.br", hashed]
    );
    await db.run(
        "INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)",
        ["Clean Architecture", 997.0, 1, "Docker", 497.0, 1]
    );
    await db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]);
    await db.run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [1, 997.0, "PAID"]
    );
    return db;
}

module.exports = { createDatabase };
