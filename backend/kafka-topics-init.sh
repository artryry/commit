#!/bin/bash

while ! /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list > /dev/null 2>&1; do
    echo "Waiting for Kafka to start..."
    sleep 3
done

# ./opt/bitnami/kafka/bin/

echo "Kafka is ready! Creating topics..."

# Creating topics
./opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --create --topic public-key
./opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --create --topic auth-users

echo "Topics created!"
