package software.architecture.microkernel.platform;

public abstract class AbstractPlugin implements Plugin {
    protected Greeter greeter;

    public AbstractPlugin(Greeter greeter) {
        this.greeter = greeter;
    }
}
