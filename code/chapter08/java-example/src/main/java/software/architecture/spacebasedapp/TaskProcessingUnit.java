package software.architecture.spacebasedapp;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class TaskProcessingUnit extends Thread {

    private boolean wait = true;

    private Map<String, Task> tasks = new ConcurrentHashMap<String, Task>();
    private String bufferKey;

    public TaskProcessingUnit(Map<String, Task> data) {
        this.tasks.putAll(data);
    }

    public void execute(String key) throws InterruptedException {
        bufferKey = key;
        synchronized (this) {
            this.notify();
        }
    }

    public Map<String, Task> getData() {
        return tasks;
    }

    @Override
    public void run() {
        while (wait) {
            synchronized (this) {
                try {
                    this.wait();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }

            Task task = tasks.get(bufferKey);
            if (task == null)
                continue;
            System.out.println(TaskProcessingUnit.this.getName() + ": Working on TaskID = " + task.getId() + " ... ");
            for (int i = 0; i < 100000000; i++) {
                task.setData(Integer.valueOf(task.getData().toString()) + 1);
            }
            System.out.println(TaskProcessingUnit.this.getName() + ": TaskID = " + task.getId() + " Done");
        }
    }

    public void terminate() {
        wait = false;
        synchronized (this) {
            this.notify();
        }
    }
}
