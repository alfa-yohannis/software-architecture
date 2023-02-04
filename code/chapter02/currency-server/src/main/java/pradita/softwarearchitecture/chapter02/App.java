package pradita.softwarearchitecture.chapter02;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
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

    @Autowired
    private RateRepository rateRepository;

    public static void main(String[] args) {
        // System.out.println( "Hello World!" );
        SpringApplication.run(App.class, args);

        
    }

    @RequestMapping("/")
    String home() {
        return "Hello World!";
    }

    /**
     * http://localhost:8080/addrate?from=USD&to=IDR&rate=15000
     * @param from
     * @param to
     * @param rate
     * @return
     */
    @RequestMapping(path = "/addrate", produces = MediaType.APPLICATION_JSON_VALUE)
    Rate addRate(String from, String to, Double rate) {

        Rate r = new Rate(from, to, rate);
        rateRepository.save(r);

        return r;
    }

    /**
     * http://localhost:8080/convert?from=USD&to=IDR&value=3
     * @param value
     * @param from
     * @param to
     * @return
     */
    @RequestMapping(path = "/convert", produces = MediaType.APPLICATION_JSON_VALUE)
    Map<String, Object> convert(Double value, String from, String to) {
        Map<String, Object> result = new HashMap<>();
        result.put("fromCurrency", from);
        result.put("toCurrency", to);
        Double rate = 0d;
        Collection<Rate> rates = rateRepository.findFirstByFromCurrencyAndToCurrency(from, to);
        if (rates.size() > 0) {
            Rate r = rates.iterator().next();
            rate = r.getRate();
        }
        result.put("rate", rate);
        result.put("value", rate * value);

        return result;
    }
}
