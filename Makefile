dev:
	uv run uvicorn backend.server.app:app --reload --port 7860

test:
	uv run pytest backend/tests -v

build:
	cd frontend && npm run build
	docker build -t goat-evolution .

up:
	docker compose up --build

validate:
	openenv validate --url http://localhost:7860 --verbose

push-space:
	@echo "Set your HF Space remote and run git push"
