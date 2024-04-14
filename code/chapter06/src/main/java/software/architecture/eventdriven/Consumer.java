package software.architecture.eventdriven;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import com.rabbitmq.client.CancelCallback;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.ConsumerShutdownSignalCallback;
import com.rabbitmq.client.DeliverCallback;
import com.rabbitmq.client.Delivery;
import com.rabbitmq.client.ShutdownSignalException;

public class Consumer {
	private final static String QUEUE_ID = "QUEUE-01";

	public static void main(String[] argv) throws Exception {

		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost("127.0.0.1");
		Connection connection = factory.newConnection();
		Channel channel = connection.createChannel();

		channel.queueDeclare(QUEUE_ID, false, false, false, null);

		DeliverCallback deliverCallback = new DeliverCallback() {
			@Override
			public void handle(String consumerTag, Delivery delivery) throws IOException {
				String message = new String(delivery.getBody(), StandardCharsets.UTF_8);
				System.out.println("Received " + message);
//				if (message.equals("20")) {
//					channel.abort();
//					connection.abort();
//				}
			}
		};

		channel.basicConsume(QUEUE_ID, true, deliverCallback, new CancelCallback() {
			@Override
			public void handle(String arg0) throws IOException {
				System.out.println("Cancel callback");
			}
		}, new ConsumerShutdownSignalCallback() {
			@Override
			public void handleShutdownSignal(String arg0, ShutdownSignalException arg1) {
				System.out.println("Shutdown signal");
			}
		});
	}
}