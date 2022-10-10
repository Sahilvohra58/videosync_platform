FROM python:3.8

WORKDIR /app
COPY . .

RUN bash apt_requirements.sh
RUN pip install -r requirements.txt
RUN sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml
RUN pip uninstall --yes moviepy decorator
RUN pip install moviepy==1.0.3

ENTRYPOINT ["python"]
CMD ["app.py"]
