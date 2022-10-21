FROM golang:alpine

WORKDIR /build

# Copy and download dependencies
COPY go.mod .
COPY go.sum .
RUN go mod download

# Set args
ENV VAULT_ADDR https://127.0.0.1:5430
ENV VAULT_TOKEN root
ENV AUTH_NAME admin
ENV AUTH_PASSWORD password
ENV HOST 127.0.0.1
ENV PORT 5429
ENV APP_PROTOCOL http
ENV APP_HOST ${HOST}:${PORT}

# Copy the code into the container
COPY . .

# Install swag-go
RUN go install github.com/swaggo/swag/cmd/swag

# Build the docs
RUN swag init

# Build the application
RUN go build -o revolori .

# Export port
EXPOSE 5429

# Run Revolori
CMD ./revolori -vault-address=${VAULT_ADDR} -vault-token=${VAULT_TOKEN} -auth-name=${AUTH_NAME} -auth-password=${AUTH_PASSWORD} -address ${HOST}:${PORT} -host-address ${APP_PROTOCOL}://${APP_HOST}
