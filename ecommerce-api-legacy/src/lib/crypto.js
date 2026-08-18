const bcrypt = require("bcryptjs");
const { loadSettings } = require("../config/settings");

function hashPassword(password) {
    const rounds = loadSettings().bcryptRounds;
    return bcrypt.hash(password, rounds);
}

function verifyPassword(password, hash) {
    return bcrypt.compare(password, hash);
}

module.exports = { hashPassword, verifyPassword };
