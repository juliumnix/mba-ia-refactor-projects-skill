# code-smells-project

API de E-commerce em Python/Flask refatorada para MVC pela skill `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O SQLite (`loja.db`) é criado no primeiro boot com produtos e usuários de exemplo (senhas com hash).

Copie `.env.example` e ajuste `SECRET_KEY` antes de qualquer ambiente compartilhado.
