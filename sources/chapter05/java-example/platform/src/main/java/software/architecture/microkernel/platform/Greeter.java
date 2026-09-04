package software.architecture.microkernel.platform;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.List;

public class Greeter {

    private final String version = "v1.0.1";
    private String name = "Alice";
    private final PluginManager pluginManager;

    public Greeter() {
        this.pluginManager = new PluginManager(this);
        this.pluginManager.loadPlugins();
    }

    public static void main(String[] args) {
        Greeter greeter = new Greeter();
        greeter.run();
    }

    public void run() {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(System.in))) {
            while (true) {
                System.out.println("Select the language to greet in:");
                List<Plugin> plugins = pluginManager.getPlugins();
                for (int i = 0; i < plugins.size(); i++) {
                    System.out.println((i + 1) + ". " + plugins.get(i).getFriendlyName());
                }
                System.out.println("0. Quit");
                System.out.print("Input: ");

                int menu = Integer.parseInt(reader.readLine()) - 1;
                if (menu == -1) break;

                if (menu >= 0 && menu < plugins.size()) {
                    System.out.println("\n" + plugins.get(menu).sayHello(name) + "\n");
                } else {
                    System.out.println("Invalid selection. Try again.");
                }
            }

            System.out.println("Quit. Thanks for playing!");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public String getPlatformVersion() {
        return version;
    }

    public String getName() {
        return name;
    }
}
