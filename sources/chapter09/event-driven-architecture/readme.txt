How to Run the Kafka Event-Driven Application

1. Start Kafka and Zookeeper using Docker Compose:
Run the following command to start Kafka and Zookeeper in detached mode:
docker-compose up

2. Open two separate terminals:
- In the first terminal, run the consumer:
cargo run -- consumer
- In the second terminal, run the producer:
cargo run -- producer

3. Stopping the system:
- To stop the consumer and producer, press Ctrl+C in each terminal.
- To stop the Kafka and Zookeeper containers:
docker-compose down

4. Notes:
- Ensure Docker and Docker Compose are installed on your machine.
- Make sure the docker-compose.yml file is correctly configured in your project folder.
- The Rust application expects Kafka to be accessible at localhost:9092.

5. Summary:
| Step            | Action                         |
|:----------------|:-------------------------------|
| Start Docker    | docker-compose up              |
| Terminal 1      | cargo run -- consumer          |
| Terminal 2      | cargo run -- producer          |
| Stop Docker     | docker-compose down            |
