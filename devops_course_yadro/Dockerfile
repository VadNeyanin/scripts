FROM golang:1.25.8@sha256:dfae680962532eeea67ab297f1166c2c4e686edb9a8f05f9d02d96fc9191833e AS build
WORKDIR /app
COPY . /app/
RUN go mod tidy && CGO_ENABLED=0 go build -o /go/bin/app

FROM gcr.io/distroless/static-debian12:nonroot@sha256:a9329520abc449e3b14d5bc3a6ffae065bdde0f02667fa10880c49b35c109fd1 AS executor
COPY --from=build /go/bin/app /

LABEL maintainer="v.neyanin"
LABEL version="0.1.0"
LABEL service="currency"
EXPOSE 8000

CMD ["/app"]
