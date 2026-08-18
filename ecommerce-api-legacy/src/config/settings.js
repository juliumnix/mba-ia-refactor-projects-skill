function loadSettings() {
    return {
        port: Number(process.env.PORT) || 3000,
        paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "pk_test_dev_only",
        smtpUser: process.env.SMTP_USER || "dev@localhost",
        dbUser: process.env.DB_USER || "dev",
        dbPass: process.env.DB_PASS || "dev-only-change-me",
        visaPrefix: process.env.VISA_PREFIX || "4",
        bcryptRounds: Number(process.env.BCRYPT_ROUNDS) || 10,
    };
}

module.exports = { loadSettings };
