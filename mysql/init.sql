CREATE DATABASE IF NOT EXISTS llama_index;

USE llama_index;

CREATE TABLE IF NOT EXISTS travel_insights (
  id INT AUTO_INCREMENT PRIMARY KEY,
  region VARCHAR(120) NOT NULL,
  signal VARCHAR(255) NOT NULL,
  metric_value DECIMAL(10, 2) NOT NULL,
  observed_at DATE NOT NULL
);

INSERT INTO travel_insights (region, signal, metric_value, observed_at) VALUES
  ('SEA', 'flight_search_growth', 18.4, '2025-04-01'),
  ('EU', 'hotel_price_index', 6.8, '2025-04-01'),
  ('NA', 'booking_cancellation_rate', 2.1, '2025-04-01');
