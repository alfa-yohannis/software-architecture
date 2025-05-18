package software.architecture.microservice.service;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import software.architecture.microservice.entity.Employee;
import software.architecture.microservice.repository.EmployeeRepo;
import software.architecture.microservice.response.EmployeeResponse;
import software.architecture.microservice.response.PerformanceResponse;
import software.architecture.microservice.response.EmployeePerformanceResponse;

import java.util.Optional;

/***
 * This class work as the employee service that maps employee data retrieved by
 * the EmployeeRepo and map it into EmployeeResponse.
 */
public class EmployeeService {

    /***
     * @Autowired is used in Spring to automatically inject dependencies (which are
     *            objects or instances) into a Spring bean. It allows Spring to
     *            automatically resolve and inject collaborating beans into your
     *            bean by matching the data type of the bean property with one of
     *            the Spring-managed beans in the application context.
     */
    @Autowired
    private EmployeeRepo employeeRepo;

    /***
     * org.modelmapper.ModelMapper is a class provided by the ModelMapper library,
     * used for mapping data from one object to another. It facilitates the
     * conversion of complex object structures by intelligently mapping fields
     * between objects, handling nested objects, collections, and more.
     */
    @Autowired
    private ModelMapper mapper;

    @Autowired
    private RestTemplate restTemplate;

    public EmployeeResponse getEmployeeById(int id) {
        Optional<Employee> employee = employeeRepo.findById(id);
        EmployeeResponse employeeResponse = mapper.map(employee, EmployeeResponse.class);
        return employeeResponse;
    }

    public EmployeePerformanceResponse getPerformanceByEmployeeId(int id) {
        EmployeeResponse employee = this.getEmployeeById(id);
        
        // request performance data from the performance service, which is a separate service, by employee id
        ResponseEntity<PerformanceResponse> responseEntity = restTemplate.getForEntity(
                "http://localhost:8081/performance/" + employee.getId(), PerformanceResponse.class);

        PerformanceResponse performance = responseEntity.getBody();

        EmployeePerformanceResponse employeePerformance = new EmployeePerformanceResponse();
        employeePerformance.setEmployee(employee);
        employeePerformance.setPerformance(performance);

        return employeePerformance;
    }

}
