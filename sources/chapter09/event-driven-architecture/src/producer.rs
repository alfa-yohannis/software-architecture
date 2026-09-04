use rdkafka::config::ClientConfig;
use rdkafka::producer::{FutureProducer, FutureRecord};
use std::io::{self, Write};
use std::time::Duration;


// cargo run -- producer

pub async fn run_producer() {
    let producer: FutureProducer = ClientConfig::new()
        .set("bootstrap.servers", "localhost:9092")
        .create()
        .expect("Producer creation error");

    println!("✏️  Type messages to send. Type 'exit' to quit.");

    loop {
        print!("> ");
        io::stdout().flush().unwrap(); // flush to show prompt immediately

        let mut input = String::new();
        io::stdin()
            .read_line(&mut input)
            .expect("Failed to read input");

        let message = input.trim(); // remove newline

        if message.eq_ignore_ascii_case("exit") {
            println!("👋 Exiting producer...");
            break;
        }

        let delivery_status = producer
            .send(
                FutureRecord::to("order-events").payload(message).key("key"),
                Duration::from_secs(0),
            )
            .await;

        println!("✅ Sent: {:?}\n", delivery_status);
    }
}
