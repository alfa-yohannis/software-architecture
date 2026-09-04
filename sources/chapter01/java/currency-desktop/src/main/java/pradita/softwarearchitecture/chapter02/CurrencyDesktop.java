package pradita.softwarearchitecture.chapter02;

import java.awt.Point;
import java.awt.GraphicsEnvironment;
import java.awt.EventQueue;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.HashMap;
import java.util.Map;

import javax.swing.DefaultComboBoxModel;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.border.EmptyBorder;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/***
 * Main Form
 * 
 * @author Alfa Yohannis
 *
 */
public class CurrencyDesktop extends JFrame {

	private static final long serialVersionUID = 1L;

	private JPanel contentPane;
	private JTextField textFieldValue;

	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					CurrencyDesktop frame = new CurrencyDesktop();
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
	public CurrencyDesktop() {
		setTitle("Currency Converter");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 493, 130);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		contentPane.setLayout(null);

		Point centerPoint = GraphicsEnvironment.getLocalGraphicsEnvironment().getCenterPoint();
		this.setLocation(centerPoint.x - (int) this.getSize().getWidth() / 2,
		    centerPoint.y - (int) this.getSize().getHeight() / 2);

		JLabel labelFrom = new JLabel("From");
		labelFrom.setFont(new Font("SansSerif", Font.PLAIN, 20));
		labelFrom.setBounds(16, 20, 63, 16);
		contentPane.add(labelFrom);

		JComboBox<String> comboBoxFrom = new JComboBox<String>();
		comboBoxFrom.setFont(new Font("SansSerif", Font.PLAIN, 20));
		labelFrom.setLabelFor(comboBoxFrom);
		comboBoxFrom.setModel(new DefaultComboBoxModel<String>(new String[] { "USD", "GBP", "JPY" }));
		comboBoxFrom.setBounds(81, 15, 111, 26);
		contentPane.add(comboBoxFrom);

		JLabel labelTo = new JLabel("To");
		labelTo.setFont(new Font("SansSerif", Font.PLAIN, 20));
		labelTo.setBounds(16, 53, 63, 16);
		contentPane.add(labelTo);

		JComboBox<String> comboBoxTo = new JComboBox<String>();
		comboBoxTo.setFont(new Font("SansSerif", Font.PLAIN, 20));
		labelTo.setLabelFor(comboBoxTo);
		comboBoxTo.setModel(new DefaultComboBoxModel(new String[] {"IDR", "GBP"}));
		comboBoxTo.setBounds(81, 48, 111, 26);
		contentPane.add(comboBoxTo);

		textFieldValue = new JTextField();
		textFieldValue.setText("1.0");
		textFieldValue.setHorizontalAlignment(SwingConstants.RIGHT);
		textFieldValue.setFont(new Font("SansSerif", Font.PLAIN, 20));
		textFieldValue.setBounds(204, 14, 112, 28);
		contentPane.add(textFieldValue);
		textFieldValue.setColumns(10);

		JLabel lblConvertedValue = new JLabel("");
		lblConvertedValue.setFont(new Font("SansSerif", Font.PLAIN, 20));
		lblConvertedValue.setHorizontalAlignment(SwingConstants.RIGHT);
		lblConvertedValue.setBounds(204, 48, 112, 26);
		contentPane.add(lblConvertedValue);

		JButton btnConvert = new JButton("Convert");
		btnConvert.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				try{

				Map<String,String> params = new HashMap<>();
				params.put("from", comboBoxFrom.getSelectedItem().toString());
				params.put("to", comboBoxTo.getSelectedItem().toString());
				params.put("value", textFieldValue.getText());
				String paramString = getParamsString(params);
				String getUrl = "http://localhost:8080/convert?" + paramString;
				double convertedValue = getAmount(getUrl);
				lblConvertedValue.setText(String.valueOf(convertedValue));

				} catch(Exception exception){
					exception.printStackTrace();
				}
			}
		});
		btnConvert.setFont(new Font("SansSerif", Font.PLAIN, 20));
		btnConvert.setBounds(322, 14, 132, 27);
		contentPane.add(btnConvert);
	}

	// ---------------------------------------//

	private ObjectMapper mapper = new ObjectMapper();

	public double getAmount(String getUrl) throws IOException {
		URL obj = new URL(getUrl);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();
		con.setRequestProperty("accept", "application/json");
		InputStream inputStream = con.getInputStream();
		InputStreamReader inputStreamReader = new InputStreamReader(inputStream);
		BufferedReader in = new BufferedReader(inputStreamReader);
		String inputLine;
		StringBuffer response = new StringBuffer();
		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();
		con.disconnect();
		String json = response.toString();

		JsonNode node = mapper.readTree(json);
		String value = node.get("value").asText();
		return Double.parseDouble(value);
	}

	public static String getParamsString(Map<String, String> params)
			throws UnsupportedEncodingException {
		StringBuilder result = new StringBuilder();

		for (Map.Entry<String, String> entry : params.entrySet()) {
			result.append(URLEncoder.encode(entry.getKey(), "UTF-8"));
			result.append("=");
			result.append(URLEncoder.encode(entry.getValue(), "UTF-8"));
			result.append("&");
		}

		return result.toString();
	}
}
