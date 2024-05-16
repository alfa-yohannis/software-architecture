package software.architecture.microservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import software.architecture.microservice.response.EmployeePerformanceResponse;
import software.architecture.microservice.response.EmployeeResponse;
import software.architecture.microservice.service.EmployeeService;

/***
 * @RestController simplifies the development of RESTful web services. The
 *                 controller that receives requests and return the response.
 */
@RestController
public class EmployeeController {

    @Autowired
    private EmployeeService employeeService;

    @GetMapping("/employees/{id}")
    private ResponseEntity<EmployeeResponse> getEmployeeDetails(@PathVariable("id") int id) {
        EmployeeResponse employee = employeeService.getEmployeeById(id);
        return ResponseEntity.status(HttpStatus.OK).body(employee);
    }
    
    @GetMapping("/employees/performance/{id}")
    private ResponseEntity<EmployeePerformanceResponse> getEmployeePerformance(@PathVariable("id") int id) {
        EmployeePerformanceResponse employeePerformance = employeeService.getPerformanceByEmployeeId(id);
        return ResponseEntity.status(HttpStatus.OK).body(employeePerformance);
    }
    
}
