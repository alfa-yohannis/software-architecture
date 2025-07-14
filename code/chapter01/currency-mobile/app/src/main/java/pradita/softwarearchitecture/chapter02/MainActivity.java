package pradita.softwarearchitecture.chapter02;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.w3c.dom.Text;

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

public class MainActivity extends AppCompatActivity {

    private ObjectMapper mapper = new ObjectMapper();
    private Spinner fromSpinner;
    private Spinner toSpinner;
    private EditText fromValue;
    private TextView toValue;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        fromSpinner = (Spinner) findViewById(R.id.fromSpinner);
        ArrayAdapter<CharSequence> fromAdapter = ArrayAdapter
                .createFromResource(this, R.array.from_currencies,
                        android.R.layout.simple_spinner_item);
        fromAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        fromSpinner.setAdapter(fromAdapter);

        toSpinner = (Spinner) findViewById(R.id.toSpinner);
        ArrayAdapter<CharSequence> toAdapter = ArrayAdapter
                .createFromResource(this, R.array.to_currencies,
                        android.R.layout.simple_spinner_item);
        toAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        toSpinner.setAdapter(toAdapter);

        fromValue = (EditText) findViewById(R.id.fromValue);
        toValue = (TextView) findViewById(R.id.toValue);
    }

    public void convert(View view) {
        String fromCurrency = fromSpinner.getSelectedItem().toString();
        String toCurrency = toSpinner.getSelectedItem().toString();
        String originalValue = fromValue.getText().toString();

        try {
            Thread t = new Thread() {
                @Override
                public void run() {
                    try {
                        Map<String, String> params = new HashMap<>();
                        params.put("from", fromCurrency);
                        params.put("to", toCurrency);
                        params.put("value", originalValue);
                        String paramString = getParamsString(params);
                        String getUrl = "http://192.168.67.210:8080/convert?" + paramString;
                        double convertedValue = getAmount(getUrl);
                        toValue.setText(String.valueOf(convertedValue));
                    } catch (UnsupportedEncodingException e) {
                        throw new RuntimeException(e);
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                }
            };
            t.start();


        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }


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