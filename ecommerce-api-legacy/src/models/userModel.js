function createUserModel(db) {
    return {
        findByEmail(email) {
            return db.get("SELECT id, name, email FROM users WHERE email = ?", [email]);
        },
        create({ name, email, passwordHash }) {
            return db.run(
                "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
                [name, email, passwordHash]
            );
        },
        async deleteById(userId) {
            await db.exec("BEGIN");
            try {
                await db.run(
                    `DELETE FROM payments WHERE enrollment_id IN (
                        SELECT id FROM enrollments WHERE user_id = ?
                    )`,
                    [userId]
                );
                await db.run("DELETE FROM enrollments WHERE user_id = ?", [userId]);
                const result = await db.run("DELETE FROM users WHERE id = ?", [userId]);
                await db.exec("COMMIT");
                return result;
            } catch (err) {
                await db.exec("ROLLBACK");
                throw err;
            }
        },
    };
}

module.exports = { createUserModel };
