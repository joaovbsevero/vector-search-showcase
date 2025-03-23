# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.lock .
RUN pip install --upgrade pip && pip install uv
RUN uv pip install -r requirements.lock --system 

COPY ./.env .
COPY ./app .

ENV STREAMLIT_PORT=8501
ENV STREAMLIT_ADDRESS=0.0.0.0

CMD ["sh", "-c", "streamlit run ./app/interface.py --server.port=$VECTOR_SEARCH_APP_STREAMLIT_SERVER_PORT --server.address=$VECTOR_SEARCH_APP_STREAMLIT_SERVER_ADDRESS"]
