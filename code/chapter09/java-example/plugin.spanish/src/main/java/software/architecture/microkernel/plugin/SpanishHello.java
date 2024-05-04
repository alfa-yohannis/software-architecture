package software.architecture.microkernel.plugin;

import software.architecture.microkernel.platform.Greeter;
import software.architecture.microkernel.platform.Plugin;

public class SpanishHello extends Plugin {

    public SpanishHello(Greeter greeter) {
        super(greeter);
        this.greeter = greeter;
        System.out.println(this.getFriendlyName() + " is loaded by Greeter " + greeter.getPlatformVersion());
    }

    @Override
    public String getFriendlyName() {
        return "Greet in Spanish";
    }

    @Override
    public String sayHello(String name) {
        String hello = "Hola, " + name + "!";
//        System.out.println(hello);
        return hello;
    }

    public Greeter getGreeter() {
        return greeter;
    }

}
