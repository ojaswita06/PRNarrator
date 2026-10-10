.PHONY: install test run-api run-ui docker-up docker-down

install:
    python -m pip install -r requirements.txt

test:
    python -m pytest -q

run-api:
    uvicorn app.main:app --reload

run-ui:
    streamlit run frontend/app.py

docker-up:
    docker compose up --build -d

docker-down:
    docker compose down
