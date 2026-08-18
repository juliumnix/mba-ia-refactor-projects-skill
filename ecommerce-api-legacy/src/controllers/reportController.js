function createReportController({ models }) {
    return {
        async financialReport(_req, res, next) {
            try {
                const report = await models.report.financialReport();
                res.json(report);
            } catch (err) {
                next(err);
            }
        },
    };
}

module.exports = { createReportController };
