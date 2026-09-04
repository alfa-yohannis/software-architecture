package software.architecture.microkernel.plugin;

import software.architecture.microkernel.platform.Greeter;
import software.architecture.microkernel.platform.AbstractPlugin;

public class SpanishHello extends AbstractPlugin {

    public SpanishHello(Greeter greeter) {
        super(greeter);
        System.out.println(getFriendlyName() + " is loaded by Greeter " + greeter.getPlatformVersion());
    }

    @Override
    public String getFriendlyName() {
        return "Greet in Spanish";
    }

    @Override
    public String sayHello(String name) {
        return "Hola, " + name + "!";
    }
}
