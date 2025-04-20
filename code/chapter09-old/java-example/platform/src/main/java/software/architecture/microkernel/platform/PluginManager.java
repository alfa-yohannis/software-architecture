package software.architecture.microkernel.platform;

import java.io.File;
import java.io.InputStream;
import java.lang.reflect.Constructor;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.*;

public class PluginManager {

    private final Greeter greeter;
    private final List<Plugin> plugins = new ArrayList<>();

    public PluginManager(Greeter greeter) {
        this.greeter = greeter;
    }

    public void loadPlugins() {
        try {
            File pluginDir = new File("plugins");
            if (!pluginDir.exists() || !pluginDir.isDirectory()) {
                System.out.println("No plugins directory found.");
                return;
            }

            File[] jarFiles = pluginDir.listFiles((dir, name) -> name.endsWith(".jar"));
            if (jarFiles == null || jarFiles.length == 0) {
                System.out.println("No plugins found.");
                return;
            }

            for (File jar : jarFiles) {
                URLClassLoader classLoader = new URLClassLoader(new URL[]{jar.toURI().toURL()}, getClass().getClassLoader());
                InputStream propertiesInputStream = classLoader.getResourceAsStream("plugin.properties");

                if (propertiesInputStream == null) {
                    System.out.println("Missing plugin.properties in " + jar.getName());
                    continue;
                }

                Properties properties = new Properties();
                properties.load(propertiesInputStream);
                String mainClassName = properties.getProperty("mainclass");

                if (mainClassName == null || mainClassName.isEmpty()) {
                    System.out.println("Invalid mainclass entry in " + jar.getName());
                    continue;
                }

                Class<?> classToLoad = Class.forName(mainClassName, true, classLoader);
                Class<? extends Plugin> pluginClass = classToLoad.asSubclass(Plugin.class);
                Constructor<? extends Plugin> constructor = pluginClass.getDeclaredConstructor(Greeter.class);
                Plugin plugin = constructor.newInstance(greeter);
                plugins.add(plugin);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public List<Plugin> getPlugins() {
        return plugins;
    }
}
