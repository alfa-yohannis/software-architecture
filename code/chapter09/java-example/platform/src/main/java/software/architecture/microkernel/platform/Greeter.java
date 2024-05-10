package software.architecture.microkernel.platform;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Method;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;

public class Greeter {

    private static final Greeter greeter = new Greeter();
    private static List<Plugin> plugins = new ArrayList<Plugin>();

    private String version = "v1.0.1";
    private String name = "Alice";

    public static void main(String[] args) {

        try {
            List<File> jars = Arrays.asList(new File("plugins").listFiles()).stream()
                    .filter(f -> f.getName().endsWith(".jar")).toList();

            for (File jar : jars) {
                URLClassLoader classLoader = new URLClassLoader(new URL[] { jar.toURI().toURL() },
                        greeter.getClass().getClassLoader());
                InputStream propertiesInputStream = classLoader.getResourceAsStream("plugin.properties");
                Properties properties = new Properties();
                properties.load(propertiesInputStream);
                String mainClassName = String.valueOf(properties.get("mainclass"));
                Class<?> classToLoad = Class.forName(mainClassName, true, classLoader);
                Plugin loadedPlugin = (Plugin) classToLoad.getDeclaredConstructor(Greeter.class).newInstance(greeter);
                plugins.add(loadedPlugin);
            }

            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            int menu = -2;
            while (menu != -1) {
                System.out.println("Select the language to greet in:");
                for (Plugin plugin : plugins) {
                    System.out.println(plugins.indexOf(plugin) + 1 + "." + plugin.getFriendlyName());
                }
                System.out.println("0. Quit");
                System.out.print("Input: ");
                try {
                    String input = reader.readLine();
                    menu = Integer.valueOf(input) - 1;
                    Plugin plugin = plugins.get(menu);

                    Object result = null;
                    try {
//                    Method method = plugin.getClass().getDeclaredMethod("sayHello", String.class);
//                    Object result = method.invoke(plugin, greeter.getName());
                        result = plugin.sayHello(greeter.getName());
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    System.out.println();
                    System.out.println(result);
                    System.out.println();
                } catch (Exception e) {
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

    public void setName(String name) {
        this.name = name;
    }

}
