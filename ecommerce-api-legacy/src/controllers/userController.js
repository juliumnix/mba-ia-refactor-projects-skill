function createUserController({ models }) {
    return {
        async deleteUser(req, res, next) {
            try {
                await models.user.deleteById(req.params.id);
                res.send("Usuário deletado e registros relacionados removidos.");
            } catch (err) {
                next(err);
            }
        },
    };
}

module.exports = { createUserController };
