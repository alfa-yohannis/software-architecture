package software.architecture.spacebasedapp;

import java.util.List;
import java.util.Map.Entry;

public class Syncronizer extends Thread {

    private boolean wait = true;
    private AddTaskProcessingUnit addTaskProcessingUnit;
    private List<TaskProcessingUnit> taskProcessingUnits;

    public Syncronizer(AddTaskProcessingUnit addTaskProcessingUnit, List<TaskProcessingUnit> taskProcessingUnits) {
        this.addTaskProcessingUnit = addTaskProcessingUnit;
        this.taskProcessingUnits = taskProcessingUnits;
    }

    public void syncronize() {
        synchronized (this) {
            this.notify();
        }
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
            for (TaskProcessingUnit taskProcessingUnit : taskProcessingUnits) {
                for (Entry<String, Task> entry : addTaskProcessingUnit.getData().entrySet()) {
                    if (!taskProcessingUnit.getData().containsKey(entry.getKey())) {
                        taskProcessingUnit.getData().put(entry.getKey(), entry.getValue());
                    }
                }
            }
            // ----
        }
    }

    public void terminate() {
        wait = false;
        synchronized (this) {
            this.notify();
        }
    }
}
