const express = require("express");
const { loadSettings } = require("./config/settings");
const { createDatabase } = require("./database");
const { createCache } = require("./lib/cache");
const { createUserModel } = require("./models/userModel");
const { createCourseModel } = require("./models/courseModel");
const { createEnrollmentModel } = require("./models/enrollmentModel");
const { createPaymentModel } = require("./models/paymentModel");
const { createAuditModel } = require("./models/auditModel");
const { createReportModel } = require("./models/reportModel");
const { createCheckoutController } = require("./controllers/checkoutController");
const { createReportController } = require("./controllers/reportController");
const { createUserController } = require("./controllers/userController");
const { createApiRouter } = require("./views/apiRoutes");
const { errorHandler, notFoundHandler } = require("./middlewares/errorHandler");

async function createApp(overrides = {}) {
    const config = { ...loadSettings(), ...overrides };
    const db = overrides.db || (await createDatabase());
    const cache = overrides.cache || createCache();

    const models = {
        user: createUserModel(db),
        course: createCourseModel(db),
        enrollment: createEnrollmentModel(db),
        payment: createPaymentModel(db),
        audit: createAuditModel(db),
        report: createReportModel(db),
    };

    const checkoutController = createCheckoutController({ models, config, cache });
    const reportController = createReportController({ models });
    const userController = createUserController({ models });

    const app = express();
    app.use(express.json());
    app.use("/api", createApiRouter({ checkoutController, reportController, userController }));
    app.use(notFoundHandler);
    app.use(errorHandler);
    app.locals.config = config;
    app.locals.db = db;
    return app;
}

async function start() {
    const app = await createApp();
    const { port } = app.locals.config;
    app.listen(port, () => {
        console.log(`LMS API rodando na porta ${port}...`);
    });
}

if (require.main === module) {
    start().catch((err) => {
        console.error(err);
        process.exit(1);
    });
}

module.exports = { createApp, start };
