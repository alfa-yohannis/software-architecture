package software.architecture.spacebasedapp;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;

public class SpaceBasedApp {

    public static void main(String[] args) throws InterruptedException {
        
        Random random= new Random();
        
        Map<String, Task> initialTasks = new ConcurrentHashMap<>();
        for (int i = 0; i < 3; i++) {
            String key =  String.valueOf(Math.abs(i));
            initialTasks.put(key, new Task(key, 1));
        }
        
        AddTaskProcessingUnit addTaskProcessingUnit = new AddTaskProcessingUnit(initialTasks);
        addTaskProcessingUnit.setName("ProcessingUnit-0");
        addTaskProcessingUnit.start();
        
        TaskProcessingUnit taskProcessingUnit1 = new TaskProcessingUnit(initialTasks);
        taskProcessingUnit1.setName("ProcessingUnit-1");
        TaskProcessingUnit taskProcessingUnit2 = new TaskProcessingUnit(initialTasks);
        taskProcessingUnit2.setName("ProcessingUnit-2");
        List<TaskProcessingUnit> taskProcessingUnits = Arrays.asList(taskProcessingUnit1, taskProcessingUnit2);
        taskProcessingUnit1.start();
        taskProcessingUnit2.start();
        
        Syncronizer syncronizer = new Syncronizer(addTaskProcessingUnit, taskProcessingUnits);
        syncronizer.start();

        for (int i = 0; i < 60; i++) {
            Thread.sleep(3000);
            String key = String.valueOf(addTaskProcessingUnit.getData().size() + 1);
            addTaskProcessingUnit.addValue(key, new Task(key, 1));
            System.out.println(addTaskProcessingUnit.getName() + ": added new TaskID = " + key);

            String processKey = String.valueOf(random.nextInt(taskProcessingUnits.size()));
            TaskProcessingUnit taskProcessingUnit = taskProcessingUnits.get(Integer.valueOf(processKey));
            String taskId = String.valueOf(random.nextInt(taskProcessingUnit.getData().size()));
            try {
                taskProcessingUnit.execute(taskId);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            
            syncronizer.syncronize();
        }


        
            Thread.sleep(60000);
        
        
        syncronizer.terminate();
        addTaskProcessingUnit.terminate();
        taskProcessingUnit1.terminate();
        taskProcessingUnit2.terminate();
        
        System.out.println("Finished!");
    }
}
