FROM python:3.8-buster
ARG PROJNAME=hat-player
ENV PROJNAME=${PROJNAME}
RUN mkdir /${PROJNAME}
WORKDIR /${PROJNAME}

# python packages
COPY requirements.txt .
RUN pip install --no-dependencies --no-cache-dir -r requirements.txt

# finally
COPY . .
EXPOSE 5000

# run the command
CMD ["python", "./app.py"]
