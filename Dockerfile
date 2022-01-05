FROM python:3.9-slim

RUN apt-get update && \
  apt-get install -y git curl procps

COPY ./ /yellowsub/
RUN pip install -r /yellowsub/requirements.txt

WORKDIR /yellowsub/

CMD ["python", "-m", "http.server"]