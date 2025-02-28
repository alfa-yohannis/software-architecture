package mvp;

import java.awt.Component;

import javax.swing.JSpinner;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

public class Presenter implements ChangeListener {

	private Model model;
	private View view;

	public Model getModel() {
		return model;
	}

	public void updateModel() {

	}

	public void setModel(Model model) {
		this.model = model;
	}

	public View getView() {
		return view;
	}

	public void setView(View view) {
		this.view = view;
		this.view.setChangeListener(this);
	}

	@Override
	public void stateChanged(ChangeEvent event) {
		JSpinner spinner = (JSpinner) event.getSource();
//		System.out.println(spinner.getName() + ", value:" + spinner.getValue());
		int value = Integer.valueOf(spinner.getValue().toString());
		
		//save the value to model
		this.model.setValue(spinner.getName(), value);
		
		// get the value from model
		value = this.model.getValue(spinner.getName()) + 1;
//		System.out.println(value);

		String targetComponentName = spinner.getName() + "b";
		for (Component component : this.getView().getContentPane().getComponents()) {
			if (component instanceof JSpinner) {
				if (targetComponentName.equals(component.getName())) {
					JSpinner spin = (JSpinner) component;
					spin.setValue(value);
					break;
				}
			}
		}
	}

}
