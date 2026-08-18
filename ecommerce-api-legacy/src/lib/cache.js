function createCache() {
    const store = new Map();
    return {
        set(key, value) {
            store.set(key, value);
        },
        get(key) {
            return store.get(key);
        },
    };
}

module.exports = { createCache };
