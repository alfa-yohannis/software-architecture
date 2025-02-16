package software.architecture.microservice.service;

import java.util.Optional;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;

import software.architecture.microservice.entity.Performance;
import software.architecture.microservice.repository.PerformanceRepo;
import software.architecture.microservice.response.PerformanceResponse;

/***
 * This class work as the employee service that maps employee data retrieved by
 * the EmployeeRepo and map it into EmployeeResponse.
 */
public class PerformanceService {

    /***
     * @Autowired is used in Spring to automatically inject dependencies (which are
     *            objects or instances) into a Spring bean. It allows Spring to
     *            automatically resolve and inject collaborating beans into your
     *            bean by matching the data type of the bean property with one of
     *            the Spring-managed beans in the application context.
     */
    @Autowired
    private PerformanceRepo performanceRepo;

    /***
     * org.modelmapper.ModelMapper is a class provided by the ModelMapper library,
     * used for mapping data from one object to another. It facilitates the
     * conversion of complex object structures by intelligently mapping fields
     * between objects, handling nested objects, collections, and more.
     */
    @Autowired
    private ModelMapper mapper;

    public PerformanceResponse getPerformanceByEmployeeId(int id) {
        Optional<Performance> performance = performanceRepo.findByEmployeeId(id);
        PerformanceResponse performanceResponse = mapper.map(performance, PerformanceResponse.class);
        return performanceResponse;
    }

}
