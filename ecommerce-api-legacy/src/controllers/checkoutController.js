const { hashPassword } = require("../lib/crypto");
const { HttpError } = require("../middlewares/errorHandler");

function last4(card) {
    return String(card).slice(-4);
}

function mockCharge(card, visaPrefix) {
    return String(card).startsWith(visaPrefix) ? "PAID" : "DENIED";
}

function createCheckoutController({ models, config, cache }) {
    return {
        async checkout(req, res, next) {
            try {
                const name = req.body.usr;
                const email = req.body.eml;
                const password = req.body.pwd;
                const courseId = req.body.c_id;
                const card = req.body.card;

                if (!name || !email || !courseId || !card) {
                    throw new HttpError(400, "Bad Request");
                }

                const course = await models.course.findActiveById(courseId);
                if (!course) {
                    throw new HttpError(404, "Curso não encontrado");
                }

                let user = await models.user.findByEmail(email);
                if (!user) {
                    const passwordHash = await hashPassword(password || "123456");
                    const created = await models.user.create({
                        name,
                        email,
                        passwordHash,
                    });
                    user = { id: created.lastID, name, email };
                }

                const status = mockCharge(card, config.visaPrefix);
                if (status === "DENIED") {
                    throw new HttpError(400, "Pagamento recusado");
                }

                const enrollment = await models.enrollment.create({
                    userId: user.id,
                    courseId,
                });
                await models.payment.create({
                    enrollmentId: enrollment.lastID,
                    amount: course.price,
                    status,
                });
                await models.audit.log(`Checkout curso ${courseId} por ${user.id}`);
                cache.set(`last_checkout_${user.id}`, course.title);
                console.info("checkout_payment_attempt", {
                    courseId,
                    last4: last4(card),
                });

                res.status(200).json({
                    msg: "Sucesso",
                    enrollment_id: enrollment.lastID,
                });
            } catch (err) {
                next(err);
            }
        },
    };
}

module.exports = { createCheckoutController };
