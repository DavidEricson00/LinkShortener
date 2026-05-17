# LinkShortener

A production-style serverless URL shortener built on AWS.

Paste a long URL, get a short one back.

This project was built to explore real-world AWS architecture using serverless services, Infrastructure as Code with CloudFormation, automated deployments with GitHub Actions, observability with CloudWatch, API protection, and scalable event-driven design.


# 🚀 Technologies

- **AWS Lambda** — serverless backend functions
- **AWS API Gateway (HTTP API)** — public HTTP endpoints
- **AWS DynamoDB** — NoSQL database
- **AWS S3** — static frontend hosting
- **AWS CloudFormation** — infrastructure as code
- **GitHub Actions** — CI/CD pipeline
- **AWS CloudWatch** — dashboards, metrics, alarms
- **AWS SNS** — email alerts for failures
- **Python 3.12** — Lambda runtime
- **Pytest** — unit testing


# 🏗 Architecture

## Redirect Flow

When a user accesses a short link:

```text
User visits /xK3p9
      │
      ▼
API Gateway
      │
      ▼
Lambda (handler.py)
      │
      ▼
DynamoDB → finds slug
      │
      ▼
Returns HTTP 301 redirect
      │
      └── asynchronously invokes analytics Lambda
```


## Link Creation Flow

```text
POST /links
{
  "url": "https://long-url.com"
}
      │
      ▼
API Gateway
      │
      ▼
Lambda Authorizer validates x-api-key
      │
      ▼
Main Lambda validates payload
      │
      ▼
Generates random slug
      │
      ▼
Stores link in DynamoDB
      │
      ▼
Returns short URL
```


## Analytics Flow

Every redirect asynchronously records analytics data:

```text
Redirect request
      │
      ▼
handler.py
      │
      ▼
Invokes analytics Lambda asynchronously
      │
      ▼
analytics.py
      │
      ▼
Stores click event in clicks table
```


# 🔐 Security Features

## API Key Protection

`POST /links` is protected using:

- API Gateway Lambda Authorizer
- `x-api-key` header validation
- CloudFormation secret injection
- GitHub Actions secrets

Without a valid API key:

```text
401 Unauthorized
```

The request is blocked before reaching the main Lambda.


## Request Validation

The backend validates:

- Invalid JSON
- Missing URL
- Non-string URLs
- Oversized payloads
- Oversized URLs
- Invalid protocols

Example protections:

```python
if len(raw_body) > 4096:
    return 413

if not isinstance(url, str):
    return 400

if len(url) > 2048:
    return 400

if not url.startswith(("http://", "https://")):
    return 400
```


## API Gateway Throttling

Route-level throttling protects against spam/flooding.

### Global Limits

```yaml
DefaultRouteSettings:
  ThrottlingRateLimit: 100
  ThrottlingBurstLimit: 200
```

### Strict POST Limits

```yaml
RouteSettings:
  "POST /links":
    ThrottlingRateLimit: 5
    ThrottlingBurstLimit: 10
```

If exceeded:

```text
429 Too Many Requests
```

Requests are blocked directly at API Gateway:

- no Lambda execution
- no DynamoDB writes
- lower AWS costs


# 📊 Observability & Monitoring

## CloudWatch Dashboard

The project automatically creates a dashboard with:

- Lambda invocations
- Errors
- Duration
- Click analytics


## Error Alerts

CloudWatch alarms monitor Lambda failures.

If errors exceed the threshold:

```text
CloudWatch Alarm
      │
      ▼
SNS Topic
      │
      ▼
Email notification
```


# ⏳ Automatic Expiration (TTL)

Links automatically expire after 30 days.

Clicks analytics expire after 90 days.

DynamoDB TTL automatically removes old records using:

```yaml
TimeToLiveSpecification:
  AttributeName: expires_at
  Enabled: true
```


# 🧠 Infrastructure Design

Each Lambda has its own IAM role with least-privilege permissions.

## link-shortener Lambda

Can:

- read/write links table
- invoke analytics Lambda
- write logs

Cannot:

- access clicks table directly
- access unrelated AWS services


## analytics Lambda

Can:

- write clicks table
- write logs

Nothing else.


## authorizer Lambda

Can:

- validate API key
- write logs

Nothing else.


# 📁 Project Structure

```text
link-shortener/
├── lambda/
│   ├── handler.py
│   ├── analytics.py
│   ├── authorizer.py
│   ├── test_handler.py
│   └── test_authorizer.py
│
├── frontend/
│   └── index.html
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── template.yaml
└── README.md
```


# ⚙️ CI/CD Pipeline

Every push to `main` automatically triggers deployment.

## Pipeline Steps

### 1. Run Tests

```text
pytest lambda/test_handler.py
pytest lambda/test_authorizer.py
```

All DynamoDB/Lambda calls are mocked.

No AWS connection required.


### 2. Deploy Infrastructure

GitHub Actions deploys:

- DynamoDB tables
- Lambda functions
- API Gateway
- IAM roles
- CloudWatch dashboard
- SNS alarms

using CloudFormation.


### 3. Deploy Lambda Code

The workflow packages and uploads:

- handler.py
- analytics.py
- authorizer.py

using:

```bash
aws lambda update-function-code
```


### 4. Inject Frontend Variables

During deploy:

- API URL is injected
- API key is injected

using:

```bash
sed -i
```


### 5. Deploy Frontend

Frontend files are synced to S3 static hosting.


# 🛠 Infrastructure (CloudFormation)

All AWS infrastructure is defined in `template.yaml`.

| Resource | Description |
|---|---|
| `LinksTable` | Stores short links |
| `ClicksTable` | Stores click analytics |
| `LambdaFunction` | Main URL shortener Lambda |
| `AnalyticsFunction` | Analytics tracking Lambda |
| `AuthorizerFunction` | API key validator |
| `ApiGateway` | HTTP API |
| `ApiAuthorizer` | Lambda authorizer |
| `RoutePost` | Protected `POST /links` |
| `RouteGet` | Public redirect route |
| `AlertTopic` | SNS alert topic |
| `ErrorAlarm` | CloudWatch alarm |
| `Dashboard` | CloudWatch metrics dashboard |


# 🔧 Setup

## Prerequisites

- AWS account
- GitHub repository
- AWS IAM user with deployment permissions


## Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_REGION` | AWS region |
| `AWS_ACCOUNT_ID` | AWS account ID |
| `ALERT_EMAIL` | Email for CloudWatch alerts |
| `API_KEY` | Secret API key for POST requests |


# 🚀 Deploy

Push to `main`.

GitHub Actions handles everything automatically.


# 🌐 Frontend URL

After deployment:

```text
http://link-shortener-{AWS_ACCOUNT_ID}.s3-website.{AWS_REGION}.amazonaws.com
```


# 🧪 Running Tests Locally

Install dependencies:

```bash
pip install pytest boto3
```

Run tests:

```bash
pytest lambda/test_handler.py lambda/test_authorizer.py -v
```
