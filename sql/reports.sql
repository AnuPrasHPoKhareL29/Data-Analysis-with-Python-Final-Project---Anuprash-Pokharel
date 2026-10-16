
-- Monthly revenue
SELECT
    strftime('%Y-%m', i.InvoiceDate) AS month,
    ROUND(SUM(ii.Revenue), 2) AS total_revenue
FROM Invoices i
JOIN InvoiceItems ii ON i.InvoiceNo = ii.InvoiceNo
GROUP BY month
ORDER BY month;

-- Top 10 countries by revenue
SELECT
    i.Country,
    ROUND(SUM(ii.Revenue), 2) AS total_revenue
FROM Invoices i
JOIN InvoiceItems ii ON i.InvoiceNo = ii.InvoiceNo
GROUP BY i.Country
ORDER BY total_revenue DESC
LIMIT 10;


-- Top 10 products by quantity sold
SELECT
    p.StockCode,
    p.Description,
    SUM(ii.Quantity) AS total_quantity
FROM Products p
JOIN InvoiceItems ii ON p.StockCode = ii.StockCode
GROUP BY p.StockCode, p.Description
ORDER BY total_quantity DESC
LIMIT 10;


-- Top 10 customers by revenue
SELECT
    c.CustomerID,
    ROUND(SUM(ii.Revenue), 2) AS total_revenue
FROM Customers c
JOIN Invoices i ON c.CustomerID = i.CustomerID
JOIN InvoiceItems ii ON i.InvoiceNo = ii.InvoiceNo
GROUP BY c.CustomerID
ORDER BY total_revenue DESC
LIMIT 10;


-- Average order value
WITH invoice_totals AS (
    SELECT
        InvoiceNo,
        SUM(Revenue) AS invoice_revenue
    FROM InvoiceItems
    GROUP BY InvoiceNo
)
SELECT
    COUNT(*) AS total_invoices,
    ROUND(AVG(invoice_revenue), 2) AS average_order_value,
    ROUND(MIN(invoice_revenue), 2) AS minimum_order_value,
    ROUND(MAX(invoice_revenue), 2) AS maximum_order_value
FROM invoice_totals;


-- Number of invoices per month
SELECT
    strftime('%Y-%m', InvoiceDate) AS month,
    COUNT(*) AS invoice_count
FROM Invoices
GROUP BY month
ORDER BY month;


-- Revenue by country and month
SELECT
    strftime('%Y-%m', i.InvoiceDate) AS month,
    i.Country,
    ROUND(SUM(ii.Revenue), 2) AS total_revenue
FROM Invoices i
JOIN InvoiceItems ii ON i.InvoiceNo = ii.InvoiceNo
GROUP BY month, i.Country
ORDER BY month, total_revenue DESC;


-- Top 10 products by revenue
SELECT
    p.StockCode,
    p.Description,
    ROUND(SUM(ii.Revenue), 2) AS total_revenue
FROM Products p
JOIN InvoiceItems ii ON p.StockCode = ii.StockCode
GROUP BY p.StockCode, p.Description
ORDER BY total_revenue DESC
LIMIT 10;


-- Repeat customers
SELECT
    c.CustomerID,
    COUNT(DISTINCT i.InvoiceNo) AS invoice_count,
    ROUND(SUM(ii.Revenue), 2) AS total_revenue
FROM Customers c
JOIN Invoices i ON c.CustomerID = i.CustomerID
JOIN InvoiceItems ii ON i.InvoiceNo = ii.InvoiceNo
GROUP BY c.CustomerID
HAVING COUNT(DISTINCT i.InvoiceNo) > 1
ORDER BY invoice_count DESC, total_revenue DESC;


-- Invoice-level sales summary
SELECT
    i.InvoiceNo,
    i.InvoiceDate,
    i.CustomerID,
    i.Country,
    COUNT(ii.InvoiceItemID) AS line_items,
    SUM(ii.Quantity) AS total_quantity,
    ROUND(SUM(ii.Revenue), 2) AS invoice_revenue
FROM Invoices i
JOIN InvoiceItems ii ON i.InvoiceNo = ii.InvoiceNo
GROUP BY i.InvoiceNo, i.InvoiceDate, i.CustomerID, i.Country
ORDER BY invoice_revenue DESC;