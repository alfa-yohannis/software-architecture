package software.architecture.microkernel.plugin;

import software.architecture.microkernel.platform.Greeter;
import software.architecture.microkernel.platform.Plugin;

public class JapaneseHello extends Plugin {

    public JapaneseHello(Greeter greeter) {
        super(greeter);
        this.greeter = greeter;
        System.out.println(this.getFriendlyName() + " is loaded by Greeter " + greeter.getPlatformVersion());
    }

    @Override
    public String getFriendlyName() {
        return "Greet in Japanese";
    }

    @Override
    public String sayHello(String name) {
        String hello = "こんにちは, " + name + "!";
//        System.out.println(hello);
        return hello;
    }

    public Greeter getGreeter() {
        return greeter;
    }

}
