-- Task 1: LEFT JOIN with Row Count Validation
-- All customers retained, orders multiply rows when customers have multiple orders.
SELECT
    c.customer_id,
    c.customer_type,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.order_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_type
ORDER BY total_spent DESC NULLS LAST;

-- Task 2: Detect Unmatched Keys
-- Customers with no orders (left side unmatched rows)
SELECT
    c.customer_id,
    c.customer_type,
    c.signup_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.signup_date;

-- Orders with no matching customer (orphaned records)
SELECT
    o.order_id,
    o.customer_id,
    o.order_date
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
ORDER BY o.order_date;

-- Task 3: Compare Join Types
-- INNER JOIN returns only matched rows.
SELECT c.customer_id, o.order_id, o.order_amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;

-- LEFT JOIN returns all customers and matched orders.
SELECT c.customer_id, o.order_id, o.order_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- FULL OUTER JOIN returns all records from both sides.
SELECT c.customer_id, o.order_id, o.order_amount
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;

-- Task 4: Multi-Table Join with 3+ Tables
SELECT
    c.customer_id,
    c.customer_type,
    o.order_id,
    o.order_date,
    oi.product_id,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
WHERE c.customer_type = 'Enterprise'
ORDER BY o.order_date DESC;

-- Task 5: Join Decision Documentation
-- customers LEFT JOIN orders: preserve all customers and attach orders when present.
-- orders LEFT JOIN order_items: preserve all orders and attach items when present.
-- Full 3-table join: preserve all customers and orders with matching line items.
-- Be careful to aggregate at order/item level to avoid double-counting when joined.
