package software.architecture.spacebasedapp;

import java.util.HashMap;
import java.util.Map;

public class AddDataProcessingUnit extends Thread {

    private boolean wait = true;
    
    private Map<String, Integer> data = new HashMap<String, Integer>();
    private Map<String, Integer> buffer = new HashMap<String, Integer>();

    public AddDataProcessingUnit(Map<String, Integer> data) {
        this.data.putAll(data);
    }

    public void addValue(String key, Integer value) {
        buffer.put(key, value);
        synchronized (this) {
            this.notify();
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
            if (buffer.isEmpty()) continue;
            data.putAll(buffer);
            System.out.println(data);
            buffer.clear();
        }
    }
    
    public void terminate() {
        wait = false;
    }
}
