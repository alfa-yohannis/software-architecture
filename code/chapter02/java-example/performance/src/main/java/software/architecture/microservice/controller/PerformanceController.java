package software.architecture.microservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import software.architecture.microservice.response.PerformanceResponse;
import software.architecture.microservice.service.PerformanceService;

/***
 * @RestController simplifies the development of RESTful web services. The
 *                 controller that receives requests and return the response.
 */
@RestController
public class PerformanceController {

    @Autowired
    private PerformanceService performanceService;

    @GetMapping("/performance/{employeeId}")
    private ResponseEntity<PerformanceResponse> getEmployeeDetails(@PathVariable("employeeId") int employeeId) {
        PerformanceResponse performance = performanceService.getPerformanceByEmployeeId(employeeId);
        if (performance == null) {
            return ResponseEntity.status(HttpStatus.NO_CONTENT).body(null);
        }
        return ResponseEntity.status(HttpStatus.OK).body(performance);
        
    }
    
}
