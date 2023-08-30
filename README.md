# Event-driven Architecture Simulator

This project simulates an event-driven architecture using microservices, message queues, and monitoring solutions. It showcases how various services interact through event-driven patterns, and provides visibility into the system's workings through comprehensive monitoring solutions.

## Prerequisites

- Docker & Docker Compose installed.
- At least 4GB of RAM allocated to Docker (due to multiple services running).

## Setup & Run

1. Clone the Repository:

```bash
git clone https://github.com/spyker77/eda.git
cd eda
```

2. Build and Run the Services:

```bash
docker compose -f docker-compose.infra.yml -f docker-compose.microservices.yml up --build
```

3. Access the Services:

- API Docs: Navigate to <http://localhost/docs>.
- Kibana: Access at <http://localhost:5601>. Remember to create a data view with an index pattern like **logstash-***.
- Grafana: Available at <http://localhost:3000>. To see the RabbitMQ dashboard, set the data source to Prometheus using the server URL <http://prometheus:9090>.

## Troubleshooting

- Ensure all services are running and check Docker logs for any errors.
- For Redis-related issues, ensure the Redis container has enough memory and isn't reaching its limit.

## Production Considerations

Before deploying this simulator in a production environment, consider the following best practices and recommendations:

### 1. Use SSL/TLS

For services that expose an API or web interface, ensure that they are served over HTTPS using SSL/TLS certificates. This encrypts the data in transit and helps protect against man-in-the-middle attacks.

### 2. Adopt Kubernetes

Consider adopting Kubernetes for container orchestration. Kubernetes offers features such as auto-scaling, rolling updates, and a robust ecosystem that can help in managing microservices deployments efficiently.

### 3. Service Mesh

Incorporate a service mesh solution like Istio or Linkerd. A service mesh provides observability, traffic management, and enhanced security for the services (like mTLS). It can handle tasks like retries, timeouts, and canary releases without changing application code.

### 4. Separate Databases

Each service should ideally have its own dedicated instance of message broker, cashing system and database. This ensures that a single instance failure or compromise does not affect all services. It also helps in scaling and managing backups for individual services efficiently.

### 5. Database Encryption

Ensure databases are encrypted both in-transit and at-rest. This provides an added layer of security, especially for sensitive data.

### 6. Backup Strategy

Regularly backup databases and configurations. Ensure that backups are encrypted and stored in a secure location. Test restoration processes periodically.

### 7. Implement Role-Based Access Control (RBAC)

Implement RBAC to control who can access what resources in your system. Ensure that users and services have the least privileges required to perform their tasks.

### 8. Network Security

Utilize network-level protection, such as firewalls or VPCs, to control which services can communicate with each other. Expose only necessary ports and services to the public.

### 9. Secure Secrets Management

Utilize a secure secrets management tool like HashiCorp Vault or AWS Secrets Manager. These tools ensure that API keys, passwords, and other secrets are securely managed and rotated.

### 10. DDOS Protection

Consider using solutions like Cloudflare or AWS WAF for publicly accessible APIs.

### 11. Monitoring & Alerts

While Grafana and Kibana are excellent for visualizations, ensure that you have set up proper alerting mechanisms that notify you of potential issues, anomalies, or service failures.

### 12. Test Resilience

Regularly test the resilience of the system using chaos engineering principles. Tools like Chaos Monkey can help introduce failures in a controlled environment to ensure your system can handle them gracefully.

### 13. User Data & Privacy

If this system will process user data, ensure that you handle and store this data in compliance with data protection regulations (e.g., GDPR). Implement necessary features like data anonymization, right to erasure, and data export.

## Contributing

If you wish to contribute, please create a new branch, make changes, and submit a Pull Request.

## License

[MIT License](LICENSE.md)

## ➕ Possible Additions

### User Service

- Handles user registration, login, profile management.
- Manages user's payment methods.

### Product Service

- Lists available products, details, prices, and inventory status.
- Can be enhanced to include features like product search, reviews, and ratings.

### Cart Service

- Allows users to add/remove products to/from a cart.
- Calculates total prices, taxes, and potential discounts.

### Review and Ratings Service

- Allows users to leave feedback on products they've purchased.
- Helps in improving product discovery and trust.

### Analytics Service

- Tracks user behavior, popular products, sales trends, etc.
- Useful for business insights and making informed decisions.

### Discounts and Offers Service

- Manages promotional codes, seasonal offers, discounts, etc.
- Helps in attracting more sales and clearing stock.

### Returns and Refund Service

- Manages return requests for products.
- Processes refunds for returned products or failed deliveries.

### Reporting Service

- Generates business-critical reports on sales, returns, revenues, etc.
