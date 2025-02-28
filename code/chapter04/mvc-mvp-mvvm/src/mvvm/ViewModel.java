package mvvm;

import java.util.HashMap;
import java.util.Map;

public class ViewModel {

	private Model model;
	private Map<String, ViewModelProperty> viewModelProperties = new HashMap<>();

	public Model getModel() {
		return model;
	}

	public void updateModel() {

	}

	public void setModel(Model model) {
		this.model = model;
	}

	public Map<String, ViewModelProperty> getViewModelProperties() {
		return viewModelProperties;
	}

	public void setViewModelProperties(Map<String, ViewModelProperty> viewModelProperties) {
		this.viewModelProperties = viewModelProperties;
	}

	public void onPropertyChanged(ViewModelProperty viewModelProperty) {
//		System.out.println(viewModelProperty.getName() + ", value:" + viewModelProperty.getValue());
		int value = Integer.valueOf(viewModelProperty.getValue().toString());
		// save value to model
		this.model.setValue(viewModelProperty.getName(), value);
		// get value from model
		value = this.model.getValue(viewModelProperty.getName()) + 1;
		ViewModelProperty targetProperty = viewModelProperties.get(viewModelProperty.getName() + "b");
		targetProperty.setValue(value);

	}
}
