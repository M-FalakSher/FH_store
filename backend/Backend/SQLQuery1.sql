-- 1. Create the Database
CREATE DATABASE FH_Store_DB;
GO

USE FH_Store_DB;
GO

-- 2. Create Independent Tables (No Foreign Keys) first

CREATE TABLE Categories (
    CategoryID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500)
);

CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) UNIQUE NOT NULL,
    Address NVARCHAR(255),
    PhoneNumber NVARCHAR(20)
);

CREATE TABLE Suppliers (
    SupplierID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(100) NOT NULL,
    ContactPerson NVARCHAR(100),
    Email NVARCHAR(100),
    PhoneNumber NVARCHAR(20),
    Address NVARCHAR(255)
);

CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL, -- Store hashed passwords, not plain text!
    Role NVARCHAR(50) DEFAULT 'Staff',     -- e.g., 'Admin', 'Manager', 'Staff'
    MobileNumber NVARCHAR(20),
    CreatedAt DATETIME DEFAULT GETDATE(),
    LastLogin DATETIME
);

-- 3. Create Tables with Foreign Keys

CREATE TABLE Products (
    ProductID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(MAX),
    SKU NVARCHAR(50) UNIQUE NOT NULL,
    CategoryID INT,
    Price DECIMAL(10, 2) NOT NULL,
    Weight DECIMAL(10, 2),
    ImageUrl NVARCHAR(255),
    Status NVARCHAR(20) DEFAULT 'Active',
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

CREATE TABLE Inventory (
    InventoryID INT PRIMARY KEY IDENTITY(1,1),
    ProductID INT UNIQUE, -- One inventory record per product
    QuantityOnHand INT DEFAULT 0,
    MinStockLevel INT DEFAULT 10,
    Location NVARCHAR(100), -- e.g., 'Aisle 3, Shelf B'
    LastUpdated DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

CREATE TABLE Supplier_Product (
    SupplierID INT,
    ProductID INT,
    PRIMARY KEY (SupplierID, ProductID),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

CREATE TABLE Orders (
    OrderID INT PRIMARY KEY IDENTITY(1,1),
    CustomerID INT,
    UserID INT, -- The staff member who processed the order (optional)
    OrderDate DATETIME DEFAULT GETDATE(),
    Status NVARCHAR(50) DEFAULT 'Pending', -- 'Pending', 'Shipped', 'Delivered'
    TotalAmount DECIMAL(10, 2),
    ShippingAddress NVARCHAR(255),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE OrderDetails (
    OrderDetailID INT PRIMARY KEY IDENTITY(1,1),
    OrderID INT,
    ProductID INT,
    QuantityOrdered INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

CREATE TABLE Payments (
    PaymentID INT PRIMARY KEY IDENTITY(1,1),
    OrderID INT,
    PaymentDate DATETIME DEFAULT GETDATE(),
    Amount DECIMAL(10, 2),
    PaymentMethod NVARCHAR(50), -- 'Credit Card', 'Cash', 'PayPal'
    Status NVARCHAR(50), -- 'Completed', 'Failed'
    TransactionReference NVARCHAR(100),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
);

CREATE TABLE Shipments (
    ShipmentID INT PRIMARY KEY IDENTITY(1,1),
    OrderID INT,
    ShippingProvider NVARCHAR(100), -- 'FedEx', 'DHL'
    TrackingNumber NVARCHAR(100),
    ShipmentDate DATETIME,
    ExpectedDeliveryDate DATETIME,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
);

CREATE TABLE Receiving (
    ReceivingID INT PRIMARY KEY IDENTITY(1,1),
    SupplierID INT,
    ProductID INT,
    QuantityReceived INT,
    ReceivingDate DATETIME DEFAULT GETDATE(),
    ReceivedByUserID INT,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
    FOREIGN KEY (ReceivedByUserID) REFERENCES Users(UserID)
);
GO

-- 4. Insert some Dummy Data to test with

INSERT INTO Categories (Name, Description) VALUES ('Electronics', 'Gadgets and devices'), ('Furniture', 'Office and Home Furniture');

INSERT INTO Products (Name, SKU, CategoryID, Price, Status) 
VALUES 
('Mechanical Keyboard', 'MK-001', 1, 120.00, 'Active'),
('Ergonomic Chair', 'EC-500', 2, 250.00, 'Active');

INSERT INTO Inventory (ProductID, QuantityOnHand, Location) 
VALUES 
(1, 50, 'Warehouse A'),
(2, 15, 'Warehouse B');

SELECT * FROM Products;
SELECT * FROM Inventory;

-- Insert a test Admin user
-- The PasswordHash below is for "admin123"
INSERT INTO Users (Name, Email, PasswordHash, Role, CreatedAt)
VALUES ('System Admin', 'admin@store.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWJwM/lqw3.W.yS3.w/d.K1.T1.T2', 'Admin', GETDATE());

-- Insert a test Staff user
-- The PasswordHash below is for "staff123"
INSERT INTO Users (Name, Email, PasswordHash, Role, CreatedAt)
VALUES ('John Staff', 'staff@store.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWJwM/lqw3.W.yS3.w/d.K1.T1.T2', 'Staff', GETDATE());
UPDATE Users
SET PasswordHash = 'PASTE_YOUR_NEW_HASH_HERE'
WHERE Email = 'admin@store.com';

UPDATE Users
SET PasswordHash = '$2b$12$W4lVkeY8WxFtdnqAaTR0geH0XxAfaXGu5N0ssCQWfozvO5gw4CYm.'
WHERE Email = 'admin@store.com';

insert into Customers(Name,Email) Values ('Test Customer','test@test.com')
