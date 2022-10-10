FROM python:3.8

COPY . /app
WORKDIR /app

RUN bash apt_requirements.sh
RUN pip install --upgrade -r requirements.txt
RUN sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml
RUN pip uninstall --yes moviepy decorator
RUN pip install moviepy==1.0.3

EXPOSE $PORT
CMD gunicorn --workers=2 --bind 0.0.0.0:$PORT app:app
