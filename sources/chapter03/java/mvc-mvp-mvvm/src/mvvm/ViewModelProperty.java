package mvvm;

public class ViewModelProperty {

	private String name;
	private ViewModelPropertyChangeEvent viewModelPropertyChangeEvent;
	private Object value;
	private ViewModel viewModel;

	public ViewModelProperty(String name, ViewModel viewModel) {
		this.name = name;
		this.viewModel = viewModel;
	}

	public void setValue(Object value) {
		this.setValue(value, false);
	}
	
	public void setValue(Object value, boolean preventEventPropagation) {
		this.value = value;
		if (!preventEventPropagation) {
			this.viewModelPropertyChangeEvent.onPropertyChanged(this);
		}
	}

	public ViewModelPropertyChangeEvent getModelViewPropertyChangeEvent() {
		return viewModelPropertyChangeEvent;
	}

	public void setModelViewPropertyChangeEvent(ViewModelPropertyChangeEvent modelViewPropertyChangeEvent) {
		this.viewModelPropertyChangeEvent = modelViewPropertyChangeEvent;
	}

	public Object getValue() {
		return value;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public ViewModel getViewModel() {
		return viewModel;
	}
}
