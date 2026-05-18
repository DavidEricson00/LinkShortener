# LinkShortener

A production-style serverless URL shortener built on AWS.

Paste a long URL, get a short one back.

Built to explore real-world AWS architecture using serverless services, Infrastructure as Code with CloudFormation, automated deployments with GitHub Actions, observability with CloudWatch, API protection, and scalable event-driven design.

## 🚀 Technologies

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

## 🏗 Architecture

### Redirect Flow

```
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

### Link Creation Flow

```
POST /links { "url": "https://long-url.com" }
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
Generates random slug + stores in DynamoDB
      │
      ▼
Returns short URL
```

### Analytics Flow

```
Redirect request
      │
      ▼
handler.py
      │
      ▼
Invokes analytics Lambda asynchronously
      │
      ▼
analytics.py stores click event in clicks table
```

## 🔐 Security

### API Key Protection

`POST /links` is protected by a Lambda Authorizer that validates the `x-api-key` header before the request reaches the main Lambda. Without a valid key the request is blocked with `401 Unauthorized`.

### Request Validation

The backend validates all incoming payloads:

- Payload size limit (4096 bytes)
- Invalid JSON
- Missing or non-string URL
- URL length limit (2048 chars)
- Invalid protocol (must be http:// or https://)

### IAM Least Privilege

Each Lambda has its own IAM role with only the permissions it needs:

| Lambda | Permissions |
|---|---|
| `link-shortener` | Read/write links table, invoke analytics Lambda, write logs |
| `link-analytics` | Write clicks table, write logs |
| `link-authorizer` | Write logs only |

No role has access to resources it doesn't use.

## 📊 Observability

### CloudWatch Dashboard

Automatically created with four panels:

- Lambda invocations
- Lambda errors
- Lambda duration
- Analytics invocations (click tracking)

### Error Alerts

CloudWatch alarm monitors Lambda errors. If errors exceed the threshold, SNS sends an email notification.

## ⏳ Automatic Expiration (TTL)

DynamoDB TTL automatically removes old records:

- Links expire after **30 days**
- Click analytics expire after **90 days**

No scheduled jobs or manual cleanup needed.

## 🧠 Infrastructure Design

All resources are defined in `template.yaml` using CloudFormation.

CloudFormation generates resource names automatically — no hardcoded names. The pipeline reads actual resource names from stack Outputs after deployment and uses them dynamically.

| Resource | Description |
|---|---|
| `LinksTable` | Stores short links with TTL |
| `ClicksTable` | Stores click analytics with TTL |
| `LambdaFunction` | Main URL shortener Lambda |
| `AnalyticsFunction` | Click tracking Lambda |
| `AuthorizerFunction` | API key validator Lambda |
| `ApiGateway` | HTTP API with CORS |
| `ApiAuthorizer` | Lambda authorizer for POST route |
| `RoutePost` | Protected `POST /links` |
| `RouteGet` | Public `GET /{id}` redirect |
| `AlertTopic` | SNS topic for failure alerts |
| `ErrorAlarm` | CloudWatch alarm |
| `Dashboard` | CloudWatch metrics dashboard |

## 📁 Project Structure

```
link-shortener/
├── lambda/
│   ├── handler.py           # Main Lambda — redirect and create logic
│   ├── analytics.py         # Analytics Lambda — click tracking
│   ├── authorizer.py        # Authorizer Lambda — API key validation
│   ├── test_handler.py      # Unit tests for handler
│   └── test_authorizer.py   # Unit tests for authorizer
├── frontend/
│   └── index.html           # Static UI hosted on S3
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline
├── template.yaml            # CloudFormation — all AWS resources
└── README.md
```

## ⚙️ CI/CD Pipeline

Every push to `main` triggers the pipeline automatically.

### Steps

1. **Run tests** — pytest with mocked DynamoDB/Lambda, no AWS connection required
2. **Deploy CloudFormation** — creates or updates all AWS resources
3. **Read resource names from Outputs** — pipeline fetches actual Lambda names dynamically
4. **Deploy Lambda code** — packages and uploads handler, analytics, authorizer
5. **Inject frontend variables** — API URL and API key injected via `sed`
6. **Deploy frontend to S3** — syncs static files to S3 website hosting

## 🔧 Setup

### Prerequisites

- AWS account (free tier is sufficient)
- GitHub repository

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | Target region (e.g. `us-east-2`) |
| `AWS_ACCOUNT_ID` | 12-digit AWS account ID |
| `ALERT_EMAIL` | Email for CloudWatch failure alerts |
| `API_KEY` | Secret key to protect POST /links |

### Deploy

Push to `main`. GitHub Actions handles everything automatically.

Frontend available at:

```
http://link-shortener-{AWS_ACCOUNT_ID}.s3-website.{AWS_REGION}.amazonaws.com
```

## 🧪 Running Tests Locally

```bash
pip install pytest boto3
pytest lambda/test_handler.py lambda/test_authorizer.py -v
```

All DynamoDB and Lambda calls are mocked — no AWS connection required.

## 🎯 Purpose

Built to:

- Work hands-on with core AWS services — Lambda, API Gateway, DynamoDB, S3, IAM, SNS, CloudWatch
- Practice Infrastructure as Code with CloudFormation
- Build a CI/CD pipeline that gates deploys behind automated tests
- Understand serverless architecture and event-driven design
- Apply security principles — least privilege IAM, API key protection, input validation
- Implement observability — dashboards, alarms, and alerting
