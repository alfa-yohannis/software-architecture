package software.architecture.spacebasedapp;


import java.util.HashMap;
import java.util.Map;

public class SpaceBasedApp {

    public static void main(String[] args) throws InterruptedException {
        
        Map<String, Integer> intialData = new HashMap<>();
        AddDataProcessingUnit addDataProcessingUnit = new AddDataProcessingUnit(intialData );
        addDataProcessingUnit.start();
        Thread.sleep(1000);
        addDataProcessingUnit.addValue("A", 1);
        Thread.sleep(1000);
        addDataProcessingUnit.addValue("B", 1);
        Thread.sleep(1000);
        addDataProcessingUnit.addValue("C", 1);
        Thread.sleep(1000);
        
        addDataProcessingUnit.terminate();
    }
}
