package demo;

import java.nio.charset.StandardCharsets;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.lambda.AWSLambda;
import com.amazonaws.services.lambda.AWSLambdaClientBuilder;
import com.amazonaws.services.lambda.model.InvokeRequest;
import com.amazonaws.services.lambda.model.InvokeResult;
import com.amazonaws.services.lambda.model.ServiceException;

public class Client {

    public static void main(String[] args) {
        String functionName = "arn:aws:lambda:eu-north-1:211125412699:function:add";

        try {
            BasicAWSCredentials credentials = new BasicAWSCredentials(
                "access key", // access key
                "secret key" // secret key
            );
            
            AWSLambdaClientBuilder builder = AWSLambdaClientBuilder.standard()
                    .withCredentials(new AWSStaticCredentialsProvider(credentials))
                    .withRegion(Regions.EU_NORTH_1);

            AWSLambda client = builder.build();
            InvokeRequest req = new InvokeRequest().withFunctionName(functionName)
                    .withPayload("{\n"
                            + "  \"var1\": \"4\",\n"
                            + "  \"var2\": \"9\"\n"
                            + "}");

            InvokeResult result = client.invoke(req);

            String ans = new String(result.getPayload().array(), StandardCharsets.UTF_8);

            System.out.println(ans);

        } catch (ServiceException e) {
            System.out.println(e);
        }

        System.out.println("Finished!");

    }

}
