CREATE TABLE customer_accounts (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    balance DECIMAL(15,2) NOT NULL CHECK (balance >= 0)
);
