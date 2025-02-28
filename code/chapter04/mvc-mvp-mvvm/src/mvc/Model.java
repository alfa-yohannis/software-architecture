package mvc;

import java.awt.Component;
import java.util.HashMap;
import java.util.Map;

import javax.swing.JSpinner;

public class Model {

	private String name = null;
	private Map<String, Integer> values = new HashMap<>();
	private View view = null;

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
		Integer oldValue = values.put(key, value);

		String targetComponentName = key + "b";
		for (Component component : view.getContentPane().getComponents()) {
			if (targetComponentName.equals(component.getName())) {
				JSpinner spinner = (JSpinner) component;
				spinner.setValue(value + 1);
				break;
			}
		}
		return oldValue;
	}

	public int getValue(String key) {
		return values.get(key);
	}

	public View getView() {
		return view;
	}

	public void setView(View view) {
		this.view = view;
		this.view.setModelName(this.getName());
	}
}
