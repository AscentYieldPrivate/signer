FROM python:3.11.2
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-deps --ignore-installed -r requirements.txt
COPY ./ ./
EXPOSE 80
CMD ["/bin/bash"]