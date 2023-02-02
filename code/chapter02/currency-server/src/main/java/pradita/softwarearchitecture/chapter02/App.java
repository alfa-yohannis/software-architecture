package pradita.softwarearchitecture.chapter02;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Hello world!
 *
 */
@RestController
@SpringBootApplication
public class App {
    public static void main(String[] args) {
        // System.out.println( "Hello World!" );
        SpringApplication.run(App.class, args);
    }

    @RequestMapping("/")
    String home() {
        return "Hello World!";
    }

    @RequestMapping(path = "/currency", produces = MediaType.APPLICATION_JSON_VALUE)
    Map<String, String> currency(String value, String from, String to) {
        Map<String, String> map = new HashMap<>();
        map.put("value", value);
        map.put("from", from);
        map.put("to", to);
        map.put("to", "A");
        return map;
    }
}
