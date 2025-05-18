package software.architecture.serverless;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.io.IOUtils;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

public class LambdaRequestStreamHandler implements RequestStreamHandler {
    public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {
        String name = null;
        String jsonString = IOUtils.toString(inputStream, "UTF-8");
        try {
            ObjectMapper mapper = new ObjectMapper();
            TypeReference<HashMap<String, Object>> typeRef = new TypeReference<HashMap<String, Object>>() {
            };
            Map<String, Object> input = mapper.readValue(jsonString, typeRef);
            System.out.println("Got " + input);
            Map<String, Object> valuesMap = (Map<String, Object>) input;
            name = (String) valuesMap.get("name");
        } catch (Exception e) {
            name = jsonString;
        }
        context.getLogger().log("Input: " + String.valueOf(name));
        outputStream.write(("Hello, " + name + "!").getBytes());
    }
}