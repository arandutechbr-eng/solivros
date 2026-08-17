# Digital Publisher

Plataforma interna para digitalização, revisão e publicação de livros.

## Requisitos

- Docker
- Docker Compose
- Git

## Execução

```bash
cp .env.example .env
docker compose up --build
```

## URLs

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health checks:

```text
http://localhost:8000/health
http://localhost:8000/health/db
```

## Fluxo de utilização

```text
1. Criar livro
2. Fazer upload
3. Processar
4. Aguardar extração
5. Abrir revisão
6. Revisar
7. Aprovar
8. Publicar
9. Abrir leitor
```

O upload já inicia o processamento em background. A página do livro também tem o botão **Processar** para reexecutar extração e estruturação.

## Arquitetura

- `frontend`: React + Vite + Tailwind
- `backend`: FastAPI, services independentes, Alembic
- `postgres`: banco persistente
- `storage/original`: PDF original (nome UUID)
- `storage/extracted`: texto bruto por página em JSON
- `storage/processed`: artefatos futuros

A extração usa PyMuPDF quando o PDF tem texto selecionável. Se o volume de texto for baixo, o OCR com Tesseract entra no lugar. A interface `OCRProvider` permite trocar Tesseract por outro provedor depois, sem mudar o restante do fluxo.

## Testes

Backend:

```bash
cd backend
python -m pytest
```

Frontend:

```bash
cd frontend
npm test
```
