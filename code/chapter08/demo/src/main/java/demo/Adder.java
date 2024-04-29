package demo;

import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;

public class Adder implements RequestHandler<Object, String> {

    @SuppressWarnings("unchecked")
    @Override
    public String handleRequest(Object input, Context context) {
        
        try {
            Map<String, Object> valuesMap = (Map<String, Object>) input;

            Integer var1 = Integer.valueOf(valuesMap.get("var1").toString());
            Integer var2 = Integer.valueOf(valuesMap.get("var2").toString());

            context.getLogger().log("var1: " + String.valueOf(var1));
            context.getLogger().log("var2: " + String.valueOf(var2));
            
            return String.valueOf(var1 + var2);
        
        } catch (Exception e) {
            return e.getMessage();
        }
    }

}
