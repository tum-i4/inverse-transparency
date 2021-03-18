FROM golang:alpine

WORKDIR /build

# Copy and download dependencies
COPY go.mod .
COPY go.sum .
RUN go mod download

# Set args
ARG VAULT_ADDR
ARG VAULT_TOKEN
ARG AUTH_NAME
ARG AUTH_PASSWORD
ENV VAULT_ADDR $VAULT_ADDR
ENV VAULT_TOKEN $VAULT_TOKEN
ENV AUTH_NAME $AUTH_NAME
ENV AUTH_PASSWORD $AUTH_PASSWORD

# Copy the code into the container
COPY . .

# Build the application
RUN go build -o revolori .

# Export port
EXPOSE 5429

# Run Revolori
CMD ./revolori -vault-address=${VAULT_ADDR} -vault-token=${VAULT_TOKEN} -auth-name=${AUTH_NAME} -auth-password=${AUTH_PASSWORD}
