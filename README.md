# Event-driven architecture simulator

To run the project locally:

```bash
docker compose -f docker-compose.infra.yml -f docker-compose.microservices.yml up --build
```

👉 API docs are accessed at <http://localhost/docs>

👉 Kibana is available at <http://localhost:5601>, and don't forget to create a data view with index pattern like **logstash-***

👉 Grafana can be reached at <http://localhost:3000>, and in order to see the RabbitMQ dashboard, set the data source to Prometheus with the server URL <http://prometheus:9090>

## TODO

### User Service

- Handles user registration, login, profile management.
- Manages user's payment methods.

### Product Service

- Lists available products, details, prices, and inventory status.
- Can be enhanced to include features like product search, reviews, and ratings.

### Cart Service

- Allows users to add/remove products to/from a cart.
- Calculates total prices, taxes, and potential discounts.

### Notification Service

- Sends notifications (email, SMS, push notifications) to users.
- Order confirmation.
- Payment processed.
- Shipment tracking details.
- Payment failures.

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
