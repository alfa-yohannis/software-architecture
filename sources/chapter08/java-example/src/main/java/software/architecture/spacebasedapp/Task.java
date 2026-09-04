package software.architecture.spacebasedapp;

import java.time.Instant;

public class Task {

    private String id;
    private Object data;
    private Instant timestamp;

    public Task(String id, Object data) {
        this.id = id;
        this.data = data;
        timestamp = Instant.now();
    }

    @Override
    public String toString() {
        return "{" + id + ", " + data + ", " + timestamp + "}";
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
        timestamp = Instant.now();
    }

    public Instant getTimestamp() {
        return timestamp;
    }

}
