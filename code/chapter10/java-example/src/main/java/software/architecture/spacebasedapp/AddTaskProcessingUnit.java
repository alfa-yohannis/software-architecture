package software.architecture.spacebasedapp;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class AddTaskProcessingUnit extends Thread {

    private boolean wait = true;
    
    private Map<String, Task> tasks = new ConcurrentHashMap<String, Task>();
    private Map<String, Task> bufferTasks = new ConcurrentHashMap<String, Task>();

    public AddTaskProcessingUnit(Map<String, Task> data) {
        this.tasks.putAll(data);
    }

    public void addValue(String key, Task value) {
        bufferTasks.put(key, value);
        synchronized (this) {
            this.notify();
        }
    }

    public Map<String, Task> getData() {
        return tasks;
    }
    @Override
    public void run() {
        while(wait) {
            synchronized (this) {
                try {
                    this.wait();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            if (bufferTasks.isEmpty()) continue;
            tasks.putAll(bufferTasks);
//            System.out.println(data);
            bufferTasks.clear();
        }
    }
    
    public void terminate() {
        wait = false;
        synchronized (this) {
            this.notify();
        }
    }
}
