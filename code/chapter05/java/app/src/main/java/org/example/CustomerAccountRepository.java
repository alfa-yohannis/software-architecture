package org.example;

import java.sql.SQLException;

public interface CustomerAccountRepository {
  void save(CustomerAccount account) throws SQLException;

  CustomerAccount findById(String id) throws SQLException;
}
