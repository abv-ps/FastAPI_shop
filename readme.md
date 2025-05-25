# FastAPI shop Project

This is a minimal FastAPI shop project demonstrating 
a MongoDB database to store information for an online store:

## **Features**
1) CRUD endpoints:
   - Create: Add several products and orders into their respective collections.

   - Read: Retrieve all orders placed within the last 30 days.

   - Update: Update the stock quantity of a product after a purchase.

   - Delete: Remove products that are no longer available for sale.(GET, POST, UPDATE, DELETE)

   2) Data agregation:
   - Calculate the total number of products sold within a specific time period;
   - Use aggregation pipelines to compute the total sum of all orders for a given customer.
   3) Indexing:
   - Add indexes on the category field in the products collection to speed up queries filtering by category.
---

## Running the Project

Build and start the services with Docker Compose:
<pre>
docker-compose up --build
</pre>


### **Access services:**

The application will be available at: http://localhost:7000

## API Endpoints

### Products
POST /products/ — Create a new product

DELETE /products/unavailable/ — Delete unavailable products

### Orders
POST /orders/ — Create a new order

GET /orders/recent/ — List the 100 most recent orders

### Stats
GET /stats/sold/ — Get the total quantity of goods sold during a specified period

GET /stats/customer/{name} - Get statistics for a specific customer

## **Documentation**    

You can check the functionality at http://localhost:7000/docs after launching the project with Docker Compose.

## **User Session Management**
The project includes a Redis-backed session management system to handle user sessions efficiently.
### Features
- Session creation with unique session tokens and login timestamps.

- Session retrieval by user ID.

- Session update to refresh the last activity timestamp and extend session expiration.

- Session deletion for logging out or clearing inactive sessions.

- Automatic session expiration (TTL) after 30 minutes of inactivity.
## **Implementation Details:**
1. Sessions are stored in Redis with keys in the format session:{user_id}.

2. Each session stores:

- user_id — unique identifier of the user

- session_token — securely generated token for session identification

- login_time — timestamp when the session was created

- last_active — timestamp of the last user activity, updated on every interaction

3. Session TTL is set to 1800 seconds (30 minutes), after which the session is automatically deleted.

4. The session management logic is encapsulated in a reusable SessionManager class.

5. API endpoints for sessions are available under /session/{user_id} with support for:

- POST — create session

- GET — retrieve session

- PUT — update last active time

- DELETE — delete session
## **Event Logging with Cassandra**
The project includes a logging system using Apache Cassandra to store user activity and application events.

### Features
1. Distributed logging: Logs are stored in a fault-tolerant, horizontally scalable Cassandra cluster.

2. CQL-based access: Use CQL queries to manage and retrieve logs by type or timeframe.

3. Custom log structure:

- event_id (UUID)

- user_id (str)

- event_type (str)

- timestamp (datetime)

- metadata (optional string content)

### API Endpoints for Logs
These endpoints are available under /logs:

- POST /logs/ — Create a new log entry.
- GET /logs/ — Get logs by event type for the last 24 hours (default).
<pre>
http://localhost:7000/logs/?event_type=order_created
http://localhost:7000/logs/?event_type=order_created&hours=12
</pre>
- PUT /logs/{event_id} — Update log metadata.
- DELETE /logs/old — Delete logs older than a given number of days (default: 7).
<pre>
DELETE /logs/old?days=7
</pre>

### Implementation
- Cassandra is configured via Docker Compose and initialized with a schema using init_cassandra.

- Log operations are encapsulated in a CassandraLogManager class.
## **Database Backup**
This project includes a scheduled MongoDB backup service.

### Features
- Automatic hourly backup of MongoDB collections using mongodump.

- Backup container built from a custom image based on Ubuntu and cron.

- Backups saved to ./mongo_backup folder in the host filesystem.

### Configuration
Located in the mongo_cron/ directory with:

- backup.sh — Backup script.

- crontab.txt — Defines execution schedule.

- Custom Dockerfile to run backup service.

Limitations:
- Only the last 24 backups are retained (configurable via script logic).

- Backups are triggered every hour by default (adjustable in crontab.txt).
