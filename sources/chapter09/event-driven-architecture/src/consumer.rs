use futures::StreamExt;
use rdkafka::config::ClientConfig;
use rdkafka::consumer::{Consumer, StreamConsumer};
use rdkafka::message::Message;

pub async fn run_consumer() {
    let consumer: StreamConsumer = ClientConfig::new()
        .set("group.id", "example-group")
        .set("bootstrap.servers", "localhost:9092")
        .set("auto.offset.reset", "earliest")
        .create()
        .expect("Consumer creation error");

    consumer
        .subscribe(&["order-events"])
        .expect("Can't subscribe to specified topic");

    println!("⏳ Waiting for events...");

    let mut message_stream = consumer.stream();
    while let Some(message_result) = message_stream.next().await {
        match message_result {
            Ok(m) => {
                if let Some(payload_result) = m.payload_view::<str>() {
                    match payload_result {
                        Ok(payload) => {
                            println!("📥 New Message: {}", payload);
                        }
                        Err(e) => {
                            println!("❌ Failed to decode payload: {}", e);
                        }
                    }
                } else {
                    println!("⚠️  Received empty payload");
                }
            }
            Err(e) => println!("❌ Kafka error: {}", e),
        }
    }
}
