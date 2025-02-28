package mvvm;

import java.awt.Font;
import java.awt.GraphicsEnvironment;
import java.awt.Point;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JSpinner;
import javax.swing.border.EmptyBorder;

public class View extends JFrame {

	private static final long serialVersionUID = 1L;

	private JPanel contentPane;
	private List<Binder> bindList = new ArrayList<>();
	private JSpinner spinner001;
	private JSpinner spinner002;
	private JSpinner spinner003;

	private JSpinner spinner001b;
	private JSpinner spinner002b;
	private JSpinner spinner003b;

	/**
	 * Create the frame.
	 */
	public View() {
		setTitle("MVVM: Model-View-ViewModel");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 450, 300);
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

		Point centerPoint = GraphicsEnvironment.getLocalGraphicsEnvironment().getCenterPoint();
		this.setLocation(centerPoint.x - (int) this.getSize().getWidth() / 2,
				centerPoint.y - (int) this.getSize().getHeight() / 2);
	}

	public void bind(ViewModel viewModel) {

		bindList.add(new Binder(spinner001, viewModel.getViewModelProperties().get("spinner001")));
		bindList.add(new Binder(spinner002, viewModel.getViewModelProperties().get("spinner002")));
		bindList.add(new Binder(spinner003, viewModel.getViewModelProperties().get("spinner003")));
		bindList.add(new Binder(spinner001b, viewModel.getViewModelProperties().get("spinner001b")));
		bindList.add(new Binder(spinner002b, viewModel.getViewModelProperties().get("spinner002b")));
		bindList.add(new Binder(spinner003b, viewModel.getViewModelProperties().get("spinner003b")));

	}

}
