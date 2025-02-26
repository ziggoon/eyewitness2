FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install-deps
RUN playwright install chromium

ENTRYPOINT ["./main.py"]
