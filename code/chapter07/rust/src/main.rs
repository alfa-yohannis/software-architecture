use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use serde::{Serialize, Deserialize};
use std::env;
use std::error::Error;

#[derive(Serialize, Deserialize)]
struct Message {
    sender: String,
    content: String,
}

async fn start_server(address: &str) -> Result<(), Box<dyn Error>> {
    let listener = TcpListener::bind(address).await?;
    println!("Listening on {}", address);

    loop {
        let (mut socket, addr) = listener.accept().await?;
        println!("New connection from: {}", addr);

        tokio::spawn(async move {
            let mut buffer = vec![0; 1024];
            match socket.read(&mut buffer).await {
                Ok(size) if size > 0 => {
                    let received_msg = String::from_utf8_lossy(&buffer[..size]);
                    println!("Received: {}", received_msg);
                }
                _ => println!("Connection closed."),
            }
        });
    }
}

async fn send_message(peer_address: &str, sender_name: &str, content: &str) -> Result<(), Box<dyn Error>> {
    let mut stream = TcpStream::connect(peer_address).await?;
    
    let message = Message {
        sender: sender_name.to_string(),
        content: content.to_string(),
    };

    let serialized_msg = serde_json::to_string(&message)?;
    stream.write_all(serialized_msg.as_bytes()).await?;
    
    println!("Sent message: {}", serialized_msg);
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        println!("Usage:\n  Server mode: {} server <address>\n  Client mode: {} client <peer_address> <name> <message>", args[0], args[0]);
        return Ok(());
    }

    if args[1] == "server" {
        let address = args.get(2).cloned().unwrap_or_else(|| "127.0.0.1:8080".to_string());
        start_server(&address).await?;
    } else if args[1] == "client" {
        if args.len() < 5 {
            println!("Usage: {} client <peer_address> <name> <message>", args[0]);
            return Ok(());
        }
        let peer_address = &args[2];
        let sender_name = &args[3];
        let message = &args[4];
        send_message(peer_address, sender_name, message).await?;
    }

    Ok(())
}

