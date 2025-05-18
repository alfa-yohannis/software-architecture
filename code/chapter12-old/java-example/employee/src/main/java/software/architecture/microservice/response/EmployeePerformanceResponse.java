package software.architecture.microservice.response;

public class EmployeePerformanceResponse {

    private EmployeeResponse employee;
    private PerformanceResponse performance;

    public EmployeeResponse getEmployee() {
        return employee;
    }

    public void setEmployee(EmployeeResponse employee) {
        this.employee = employee;
    }

    public PerformanceResponse getPerformance() {
        return performance;
    }

    public void setPerformance(PerformanceResponse performance) {
        this.performance = performance;
    }
}
