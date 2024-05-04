package software.architecture.serverless;

import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;

public class LambdaMethodHandler {
    @SuppressWarnings("unchecked")
    public String handleRequest(Object input, Context context) {
        String name = null;
        if (input instanceof String) {
            name = (String) input;
        } else {
            Map<String, Object> valuesMap = (Map<String, Object>) input;
            name = (String) valuesMap.get("name");
        }
        context.getLogger().log("Input: " + String.valueOf(name));
        return "Hello, " + name + "!";
    }
}
