package org.example;

public class CustomerAccount {
  private String id;
  private String name;
  private double balance;

  public CustomerAccount(String id, String name, double initialBalance) {
    if (initialBalance < 0) {
      throw new IllegalArgumentException("Saldo awal tidak boleh negatif.");
    }
    this.id = id;
    this.name = name;
    this.balance = initialBalance;
  }

  public String getId() {
    return id;
  }

  public String getName() {
    return name;
  }

  public double getBalance() {
    return balance;
  }

  public void deposit(double amount) {
    if (amount <= 0) {
      throw new IllegalArgumentException("Jumlah deposit harus lebih dari nol.");
    }
    this.balance += amount;
  }

  public void withdraw(double amount) {
    if (amount <= 0) {
      throw new IllegalArgumentException("Jumlah penarikan harus lebih dari nol.");
    }
    if (amount > this.balance) {
      throw new IllegalArgumentException("Saldo tidak mencukupi untuk penarikan.");
    }
    this.balance -= amount;
  }
}