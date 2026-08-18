function errorHandler(err, _req, res, _next) {
    const status = err.status || 500;
    const message = status === 500 ? "Erro interno" : err.message;
    if (status === 500) {
        console.error(err);
    }
    res.status(status).json({ erro: message });
}

function notFoundHandler(_req, res) {
    res.status(404).json({ erro: "Rota não encontrada" });
}

class HttpError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

module.exports = { errorHandler, notFoundHandler, HttpError };
