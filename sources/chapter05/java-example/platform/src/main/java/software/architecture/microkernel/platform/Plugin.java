package software.architecture.microkernel.platform;

public interface Plugin {
	String getFriendlyName();

	String sayHello(String name);
}
