mod producer;
mod consumer;

use std::env;

#[tokio::main]
async fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("❗ Usage: cargo run -- [producer|consumer]");
        return;
    }

    match args[1].as_str() {
        "producer" => producer::run_producer().await,
        "consumer" => consumer::run_consumer().await,
        _ => println!("❗ Unknown argument. Use 'producer' or 'consumer'."),
    }
}
