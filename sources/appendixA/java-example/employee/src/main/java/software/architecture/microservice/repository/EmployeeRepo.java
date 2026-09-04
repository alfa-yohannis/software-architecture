package software.architecture.microservice.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import software.architecture.microservice.entity.Employee;

/***
 * EmployeeRepo extends JpaRepository<Employee, Integer> establishes an
 * interface called EmployeeRepo that extends JpaRepository, specifying Employee
 * as the entity type and Integer as the type of the entity's primary key. This
 * enables the repository to perform CRUD operations and pagination/sorting on
 * Employee entities.
 */
public interface EmployeeRepo extends JpaRepository<Employee, Integer> {

}
