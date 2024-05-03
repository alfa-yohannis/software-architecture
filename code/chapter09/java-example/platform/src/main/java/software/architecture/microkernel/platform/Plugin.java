package software.architecture.microkernel.platform;

public abstract class Plugin {

    protected Greeter greeter;
    public Plugin(Greeter greeter) {
        this.greeter = greeter;
    }

    public abstract String getFriendlyName();

    public abstract String sayHello(String name);
}
