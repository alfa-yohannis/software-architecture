package software.architecture.microkernel.plugin;

import software.architecture.microkernel.platform.Greeter;
import software.architecture.microkernel.platform.AbstractPlugin;

public class JapaneseHello extends AbstractPlugin {

    public JapaneseHello(Greeter greeter) {
        super(greeter);
        System.out.println(getFriendlyName() + " is loaded by Greeter " + greeter.getPlatformVersion());
    }

    @Override
    public String getFriendlyName() {
        return "Greet in Japanese";
    }

    @Override
    public String sayHello(String name) {
        return "こんにちは, " + name + "!";
    }
}
