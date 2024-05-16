package software.architecture.microservice.configuration;

import org.modelmapper.ModelMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

import software.architecture.microservice.service.EmployeeService;

/***
 * The @Configuration annotation signifies that the class includes methods
 * with @Bean definitions. This allows the Spring container to handle the class,
 * creating Spring Beans that can be utilized within the application. This
 * annotation is integral to the Spring Core framework.
 */

@Configuration
public class EmployeeConfig {

    @Bean
    public EmployeeService employeeBean() {
        return new EmployeeService();
    }

    @Bean
    public ModelMapper modelMapperBean() {
        return new ModelMapper();
    }
    
    @Bean
    public RestTemplate restTemplate(){
        return new RestTemplate();
    }

}
