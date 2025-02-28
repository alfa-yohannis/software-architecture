package mvi;

import java.util.HashMap;
import java.util.Map;

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

	public void handleIntent(Intent intent) {
		if (intent instanceof UpdateValueIntent) {
			UpdateValueIntent updateValueIntent = (UpdateValueIntent) intent;
			this.setValue(updateValueIntent.getSourceName(), updateValueIntent.getValue());
			int value = this.getValue(updateValueIntent.getSourceName()) + 1;
			updateSpinnerState(updateValueIntent.getTargetName(), value);
		}
	}

	private void updateSpinnerState(String targetName, int value) {
		view.updateViewState(targetName, value);
	}
}
