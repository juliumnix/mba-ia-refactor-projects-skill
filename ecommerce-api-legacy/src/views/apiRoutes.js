const express = require("express");

function createApiRouter({ checkoutController, reportController, userController }) {
    const router = express.Router();
    router.post("/checkout", checkoutController.checkout);
    router.get("/admin/financial-report", reportController.financialReport);
    router.delete("/users/:id", userController.deleteUser);
    return router;
}

module.exports = { createApiRouter };
