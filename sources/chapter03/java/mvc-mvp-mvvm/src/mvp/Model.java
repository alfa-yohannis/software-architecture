package mvp;

import java.util.HashMap;
import java.util.Map;

public class Model {

	private String name = null;
	private Map<String, Integer> values = new HashMap<>();

	public Model(String name) {
		this.name = name;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Map<String, Integer> getValues() {
		return values;
	}

	public void setValues(Map<String, Integer> values) {
		this.values = values;
	}

	public Integer setValue(String key, int value) {
		return values.put(key, value);
	}

	public int getValue(String key) {
		return values.get(key);
	}
}
