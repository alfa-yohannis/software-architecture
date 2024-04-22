package sofware.architecture.pipesandfilters;
import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.impl.DefaultCamelContext;

public class CamelPipelineExample {
    public static void main(String[] args) throws Exception {
        // Create Camel context
        DefaultCamelContext context = new DefaultCamelContext();

        // Add routes to the context
        context.addRoutes(new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                // Define a pipeline using the pipe-and-filter pattern
                from("direct:start")
                    .filter().method(FilterComponent.class, "filter")
                    .to("direct:process");

                from("direct:process")
                    .bean(ProcessorComponent.class, "process")
                    .to("direct:end");
            }
        });

        // Start the Camel context
        context.start();

        // Send a message through the pipeline
        context.createProducerTemplate().sendBody("direct:start", "Hello, Camel!");

        // Stop the Camel context
        context.close();
        context.stop();
    }
}

class FilterComponent {
    public boolean filter(String body) {
        // Filter logic: Accept messages containing "Camel"
        return body.contains("Camel");
    }
}

class ProcessorComponent {
    public String process(String body) {
        // Process the message
        return body.toUpperCase();
    }
}
