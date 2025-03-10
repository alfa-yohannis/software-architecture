package org.example;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class PostgreSQLCustomerAccountRepository implements CustomerAccountRepository {
  private Connection connection;
  
  // Konstruktor yang secara otomatis membuat koneksi ke database PostgreSQL
  public PostgreSQLCustomerAccountRepository() throws SQLException {
    this.connection = DriverManager.getConnection(
      "jdbc:postgresql://localhost:5432/customer_db", "postgres", "1234"
    );
  }
  
  // Menyimpan akun pelanggan ke dalam database
  @Override
  public void save(CustomerAccount account) throws SQLException {
    String sql = "INSERT INTO customer_accounts (id, name, balance) VALUES (?, ?, ?)";
    PreparedStatement stmt = connection.prepareStatement(sql);
    stmt.setString(1, account.getId());
    stmt.setString(2, account.getName());
    stmt.setDouble(3, account.getBalance());
    stmt.executeUpdate();
  }
  
  // Mengambil akun pelanggan berdasarkan ID
  @Override
  public CustomerAccount findById(String id) throws SQLException {
    String sql = "SELECT * FROM customer_accounts WHERE id = ?";
    PreparedStatement stmt = connection.prepareStatement(sql);
    stmt.setString(1, id);
    ResultSet rs = stmt.executeQuery();
    
    if (rs.next()) {
      return new CustomerAccount(rs.getString("id"), rs.getString("name"), rs.getDouble("balance"));
    }
    return null;
  }
}
