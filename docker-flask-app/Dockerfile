# Instructions copied from - https://hub.docker.com/_/python/
FROM python:3-onbuild

# tell the port number the container should expose
EXPOSE 5000

# attempt to re-install wsgi to fix error
CMD ["apt-get", "update"]
CMD ["apt-get", "install", "libapache2-mod-wsgi"]
# CMD ["apt-get", "update", "&&", "apt-get", "install", "-y", "build-essential", "wget", "git", "unzip"]

# install latest version of fasttext
# CMD
#     apt-get update && apt-get install -y build-essential wget git unzip
# RUN
#     wget https://github.com/facebookresearch/fastText/archive/v0.9.1.zip && unzip v0.9.1.zip && cd fastText-0.9.1 && make && \
#     git clone https://github.com/facebookresearch/fastText.git && cd fastText && pip install .
# CMD [
#     "wget", "https://github.com/facebookresearch/fastText/archive/v0.9.1.zip", "&&",
#     "unzip", "v0.9.1.zip", "&&",
#     "cd", "fastText-0.9.1", "&&",
#     "make", "&&",
#     "git", "clone", "https://github.com/facebookresearch/fastText.git", "&&",
#     "cd", "fastText", "&&",
#     "pip", "install", "."
# ]

# RUN apt-get update && apt-get install -y \
#         build-essential \
#         wget \
#         git \
#         unzip \
#         && rm -rf /var/cache/apk/*

# RUN git clone https://github.com/facebookresearch/fastText.git /tmp/fastText && \
#   rm -rf /tmp/fastText/.git* && \
#   mv /tmp/fastText/* / && \
#   cd / && \
#   make && pip install .

# WORKDIR /

# run the command
CMD ["python", "./app.py"]
