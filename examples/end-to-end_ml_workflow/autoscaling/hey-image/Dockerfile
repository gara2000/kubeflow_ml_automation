FROM alpine
RUN wget https://hey-release.s3.us-east-2.amazonaws.com/hey_linux_amd64 -O /usr/local/bin/hey && \
    chmod +x /usr/local/bin/hey
ENTRYPOINT ["hey"]