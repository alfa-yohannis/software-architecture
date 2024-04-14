package software.architecture.eventdriven;

import java.nio.charset.StandardCharsets;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

public class Producer {
	private final static String QUEUE_ID = "QUEUE-01";

	public static void main(String[] argv) throws Exception {
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost("127.0.0.1");
		try (Connection connection = factory.newConnection(); Channel channel = connection.createChannel()) {
			channel.queueDeclare(QUEUE_ID, false, false, false, null);

			for (int i = 1; i <= 20; i++) {
				String message = String.valueOf(i);
				channel.basicPublish("", QUEUE_ID, null, message.getBytes(StandardCharsets.UTF_8));
				System.out.println(" Sent " + message);
			}
		}
	}
}