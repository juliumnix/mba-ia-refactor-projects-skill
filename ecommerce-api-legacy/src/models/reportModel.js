function createReportModel(db) {
    return {
        async financialReport() {
            const rows = await db.all(
                `
                SELECT
                    c.id AS course_id,
                    c.title AS course,
                    u.name AS student,
                    p.amount AS amount,
                    p.status AS payment_status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
                ORDER BY c.id, e.id
                `
            );

            const byCourse = new Map();
            for (const row of rows) {
                if (!byCourse.has(row.course_id)) {
                    byCourse.set(row.course_id, {
                        course: row.course,
                        revenue: 0,
                        students: [],
                    });
                }
                const courseData = byCourse.get(row.course_id);
                if (!row.student) {
                    continue;
                }
                if (row.payment_status === "PAID") {
                    courseData.revenue += row.amount;
                }
                courseData.students.push({
                    student: row.student,
                    paid: row.amount || 0,
                });
            }
            return Array.from(byCourse.values());
        },
    };
}

module.exports = { createReportModel };
