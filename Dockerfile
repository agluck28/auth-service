FROM python:3.10-buster

COPY requirements.txt /

RUN pip install -r requirements.txt --no-cache-dir

WORKDIR /var/apps/authService

COPY src/ .

ENTRYPOINT ["python"]

CMD ["./authService.py", "-e", "./config/.env"]