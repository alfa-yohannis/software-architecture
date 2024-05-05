package software.architecture.spacebasedapp;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

public class IncrementProcessingUnit extends Thread {

    private boolean wait = true;
    
    private Map<String, Integer> data = new HashMap<String, Integer>();

    public IncrementProcessingUnit(Map<String, Integer> data) {
        this.data.putAll(data);
    }

    public void increment(int incrementByValue) {
        for (Entry<String, Integer> entry : data.entrySet()) {
            entry.setValue(entry.getValue() + incrementByValue);
        }
    }

    public Map<String, Integer> getData() {
        return data;
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
        }
    }
    
    public void terminate() {
        wait = false;
    }
}
