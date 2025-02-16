package software.architecture.microservice.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import software.architecture.microservice.entity.Performance;

/***
 * EmployeeRepo extends JpaRepository<Employee, Integer> establishes an
 * interface called EmployeeRepo that extends JpaRepository, specifying Employee
 * as the entity type and Integer as the type of the entity's primary key. This
 * enables the repository to perform CRUD operations and pagination/sorting on
 * Employee entities.
 */
public interface PerformanceRepo extends JpaRepository<Performance, Integer> {

    @Query("select p from Performance p where p.employeeId = :#{#employee_id}")
    Optional<Performance> findByEmployeeId(@Param("employee_id") Integer employee_id);
    
    
}
