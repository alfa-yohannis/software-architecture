package software.architecture.eventdriven;

import java.awt.EventQueue;

import javax.swing.JFrame;
import javax.swing.JButton;
import java.awt.Font;
import javax.swing.JLabel;
import javax.swing.SwingConstants;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.Color;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeEvent;

public class EventDrivenDemo extends JFrame {

	private static final long serialVersionUID = 1L;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					EventDrivenDemo frame = new EventDrivenDemo();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the frame.
	 */
	public EventDrivenDemo() {
		setBounds(100, 100, 450, 300);
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		getContentPane().setLayout(null);

		JLabel display2 = new JLabel("0");
		display2.setHorizontalAlignment(SwingConstants.CENTER);
		display2.setForeground(Color.BLACK);
		display2.setFont(new Font("Dialog", Font.BOLD, 32));
		display2.setBackground(Color.BLACK);
		display2.setBounds(241, 61, 159, 71);
		getContentPane().add(display2);

		JLabel display1 = new JLabel("0");
		display1.setForeground(Color.BLACK);
		display1.setBackground(new Color(0, 0, 0));
		display1.setHorizontalAlignment(SwingConstants.CENTER);
		display1.setFont(new Font("Dialog", Font.BOLD, 32));
		display1.setBounds(56, 60, 159, 71);
		getContentPane().add(display1);
		
		display1.addPropertyChangeListener(new PropertyChangeListener() {
			public void propertyChange(PropertyChangeEvent event) {
				if (event.getPropertyName().equals("text")) {
					int value = Integer.valueOf(event.getNewValue().toString());
					int remainder = value % 4;
					if (remainder == 0) {
						display2.setText(String.valueOf(Integer.valueOf(display2.getText()) + 1));
					}
				}
			}
		});
		

		JButton btnPushMe = new JButton("Push Me!");
		btnPushMe.setFont(new Font("Dialog", Font.BOLD, 24));
		btnPushMe.setBounds(155, 166, 159, 44);
		getContentPane().add(btnPushMe);
		btnPushMe.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				display1.setText(String.valueOf(Integer.valueOf(display1.getText()) + 1));
			}
		});
		

	}
}
