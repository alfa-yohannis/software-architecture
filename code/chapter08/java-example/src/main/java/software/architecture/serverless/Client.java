package software.architecture.serverless;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.lambda.AWSLambda;
import com.amazonaws.services.lambda.AWSLambdaClientBuilder;
import com.amazonaws.services.lambda.model.InvokeRequest;
import com.amazonaws.services.lambda.model.InvokeResult;
import com.amazonaws.services.lambda.model.ServiceException;

import java.nio.charset.StandardCharsets;

public class Client {

    public static void main(String... args) {

        String functionName = "arn:aws:lambda:eu-north-1:211125412699:function:MethodHandlerLambda";

        try {

            Regions region = Regions.EU_NORTH_1;

//            AWSLambdaClientBuilder builder = AWSLambdaClientBuilder.standard().withRegion(region);

            BasicAWSCredentials credentials = new BasicAWSCredentials(
                    "Your Amazon IaM access key", // access key
                    "Your Amazon IaM secret key"); // secret key

            AWSLambdaClientBuilder builder = AWSLambdaClientBuilder.standard()
                    .withCredentials(new AWSStaticCredentialsProvider(credentials)).withRegion(region);

            AWSLambda client = builder.build();
            InvokeRequest req = new InvokeRequest().withFunctionName(functionName)
                    .withPayload("{\n\"name\": \"Test\"\n}");
            InvokeResult result = client.invoke(req);

            String ans = new String(result.getPayload().array(), StandardCharsets.UTF_8);

            // write out the return value
            System.out.println(ans);

        } catch (ServiceException e) {
            System.out.println(e);
        }

        System.out.println("Finished!");
    }
}
