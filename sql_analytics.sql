USE upi_merchant_health;

-- overall revenue and transaction summary per merchant
SELECT
    m.merchant_id,
    m.merchant_name,
    m.category,
    m.city,
    SUM(ds.total_revenue)       AS lifetime_revenue,
    SUM(ds.transaction_count)   AS lifetime_transactions,
    AVG(ds.avg_ticket_size)     AS avg_ticket_size,
    SUM(ds.refund_count)        AS total_refunds,
    SUM(ds.failed_count)        AS total_failed,
    COUNT(ds.summary_date)      AS active_days
FROM merchants m
JOIN daily_summaries ds ON m.merchant_id = ds.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.category, m.city
ORDER BY lifetime_revenue DESC;