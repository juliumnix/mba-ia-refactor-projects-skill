from src.app import create_app

app = create_app()


if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{app.config['PORT']}")
    print("=" * 50)
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
