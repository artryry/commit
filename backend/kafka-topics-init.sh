#!/bin/bash

# Wait for Kafka to be ready
for i in {1..30}; do
    if kafka-topics --bootstrap-server kafka:9092 --list > /dev/null 2>&1; then
        echo "Kafka is ready!"
        break
    fi
    echo "Waiting for Kafka to start... (attempt $i/30)"
    sleep 2
    
    if [ $i -eq 30 ]; then
        echo "Kafka failed to start after 60 seconds"
        exit 1
    fi
done

echo "Creating topics..."

# Creating topics with explicit configuration
kafka-topics --bootstrap-server kafka:9092 \
  --create --topic user.created \
  --partitions 3 --replication-factor 1 \
  --if-not-exists

kafka-topics --bootstrap-server kafka:9092 \
  --create --topic user.deleted \
  --partitions 3 --replication-factor 1 \
  --if-not-exists

kafka-topics --bootstrap-server kafka:9092 \
  --create --topic profile.updated \
  --partitions 3 --replication-factor 1 \
  --if-not-exists

echo "Topics created!"
kafka-topics --bootstrap-server kafka:9092 --list
