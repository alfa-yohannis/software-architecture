package mvi;

import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GraphicsEnvironment;
import java.awt.Point;
import java.awt.Toolkit;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JSpinner;
import javax.swing.border.EmptyBorder;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

public class View extends JFrame {

	private static final long serialVersionUID = 1L;

	private Model model;

	private JPanel contentPane;

	public JPanel getContentPane() {
		return contentPane;
	}

	private JSpinner spinner001;
	private JSpinner spinner003;
	private JSpinner spinner002;
	private JSpinner spinner001b;
	private JSpinner spinner002b;
	private JSpinner spinner003b;
	private String modelName;

	/**
	 * Create the frame.
	 * 
	 * @param model
	 */
	public View(Model model) {
		this.model = model;
		this.model.setView(this);

		setTitle("MVP: Model-View-Intent");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 800, 600);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));

		setContentPane(contentPane);

		spinner001 = new JSpinner();
		spinner001.setName("spinner001");
		((JSpinner.DefaultEditor) spinner001.getEditor()).getTextField().setColumns(3);
		spinner001.setFont(new Font("Dialog", Font.BOLD, 32));
		contentPane.add(spinner001);

		spinner001b = new JSpinner();
		spinner001b.setEnabled(false);
		spinner001b.setName("spinner001b");
		((JSpinner.DefaultEditor) spinner001b.getEditor()).getTextField().setColumns(3);
		spinner001b.setFont(new Font("Dialog", Font.BOLD, 32));
		contentPane.add(spinner001b);

		spinner002 = new JSpinner();
		spinner002.setName("spinner002");
		((JSpinner.DefaultEditor) spinner002.getEditor()).getTextField().setColumns(3);
		spinner002.setFont(new Font("Dialog", Font.BOLD, 32));
		contentPane.add(spinner002);

		spinner002b = new JSpinner();
		spinner002b.setEnabled(false);
		spinner002b.setName("spinner002b");
		((JSpinner.DefaultEditor) spinner002b.getEditor()).getTextField().setColumns(3);
		spinner002b.setFont(new Font("Dialog", Font.BOLD, 32));
		contentPane.add(spinner002b);

		spinner003 = new JSpinner();
		spinner003.setName("spinner003");
		((JSpinner.DefaultEditor) spinner003.getEditor()).getTextField().setColumns(3);
		spinner003.setFont(new Font("Dialog", Font.BOLD, 32));
		contentPane.add(spinner003);

		spinner003b = new JSpinner();
		spinner003b.setEnabled(false);
		spinner003b.setName("spinner003b");
		((JSpinner.DefaultEditor) spinner003b.getEditor()).getTextField().setColumns(3);
		spinner003b.setFont(new Font("Dialog", Font.BOLD, 32));
		contentPane.add(spinner003b);

//		Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
//	    this.setSize(screenSize.width, screenSize.height);
	    
		Point centerPoint = GraphicsEnvironment.getLocalGraphicsEnvironment().getCenterPoint();
		this.setLocation(centerPoint.x - (int) this.getSize().getWidth() / 2,
				centerPoint.y - (int) this.getSize().getHeight() / 2);
		
		spinner001.addChangeListener(new JSpinnerChangeListenger());
		spinner002.addChangeListener(new JSpinnerChangeListenger());
		spinner003.addChangeListener(new JSpinnerChangeListenger());

	}

	public void updateViewState(String targetName, Object value) {
		for (Component component : View.this.getContentPane().getComponents()) {
			if (targetName.equals(component.getName())) {
				JSpinner spinner = (JSpinner) component;
				spinner.setValue(value);
				break;
			}
		}
	}

	public class JSpinnerChangeListenger implements ChangeListener {
		@Override
		public void stateChanged(ChangeEvent event) {
			JSpinner spinner = (JSpinner) event.getSource();
			int value = (int) spinner.getValue();
			UpdateValueIntent intent = new UpdateValueIntent(spinner.getName(), spinner.getName() + "b", value);
			View.this.model.handleIntent(intent);
		}

	}

	public String getModelName() {
		return modelName;
	}

	public void setModelName(String modelName) {
		this.modelName = modelName;
	}

	public Model getModel() {
		return model;
	}

	public void setModel(Model model) {
		this.model = model;
	}
}
