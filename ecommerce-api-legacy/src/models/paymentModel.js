function createPaymentModel(db) {
    return {
        create({ enrollmentId, amount, status }) {
            return db.run(
                "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
                [enrollmentId, amount, status]
            );
        },
    };
}

module.exports = { createPaymentModel };
