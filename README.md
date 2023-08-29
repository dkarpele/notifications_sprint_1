# Sprint 10, Notifications

### Installation

1. Clone [repo](https://github.com/dkarpele/notifications_sprint_1).
2. Create ```.env``` file according to ```.env.example```.
3. Launch the project ```docker-compose up --build```.


#### [architecture](architecture)

Architecture for the notifications service described here.

#### [notifications](notifications)

We use RabbitMQ as a broker.

**Notify email**
- POST http://127.0.0.1/api/v1/notify-email/user-sign-up - send email notification to user after signing up

**Scheduler**
- likes_for_reviews. We send users an aggregated information about likes they received for their reviews to movies during last 24 hours. 