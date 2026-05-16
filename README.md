# LinkShortener

A serverless URL shortener built on AWS. Paste a long URL, get a short one back. Built to explore core AWS services and practice Infrastructure as Code with CloudFormation and automated deployments with GitHub Actions.

## 🚀 Technologies

- **AWS Lambda** — serverless function handling redirect and link creation logic
- **AWS API Gateway** — HTTP endpoint exposing the Lambda publicly
- **AWS DynamoDB** — NoSQL table storing slug → URL mappings
- **AWS S3** — static website hosting for the frontend
- **AWS CloudFormation** — all infrastructure defined and provisioned as code
- **GitHub Actions** — CI/CD pipeline running tests before every deploy
- **Python 3.12** — Lambda runtime

## 🏗 Architecture

When accessing a short link:

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
DynamoDB — finds slug → returns 301 redirect
```

When shortening a link:

```
POST /links { "url": "https://long-url.com" }
      │
      ▼
Lambda generates a random 6-char slug
      │
      ▼
DynamoDB stores { id: "xK3p9", url: "https://long-url.com" }
      │
      ▼
Returns { "short_url": "xK3p9" }
```

## 📁 Project Structure

```
link-shortener/
├── lambda/
│   ├── handler.py           # Lambda function — redirect and create logic
│   └── test_handler.py      # Unit tests with mocked DynamoDB
├── frontend/
│   └── index.html           # Static UI hosted on S3
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline
├── template.yaml            # CloudFormation — all AWS resources
└── README.md
```

## ⚙️ CI/CD Pipeline

Every push to `main` triggers the pipeline:

1. **Tests** — runs unit tests with pytest using mocked DynamoDB (no AWS credentials required)
2. **Deploy** — only runs if all tests pass
   - Deploys CloudFormation stack (DynamoDB, Lambda, API Gateway)
   - Uploads Lambda code via `update-function-code`
   - Injects the API Gateway URL into the frontend
   - Syncs frontend to S3

## 🛠 Infrastructure (CloudFormation)

All AWS resources are defined in `template.yaml`:

| Resource | Description |
|---|---|
| `LinksTable` | DynamoDB table with `id` as partition key |
| `LambdaRole` | IAM role granting Lambda access to DynamoDB and CloudWatch |
| `LambdaFunction` | Python 3.12 function with `TABLE_NAME` env var |
| `ApiGateway` | HTTP API with CORS enabled |
| `LambdaIntegration` | Connects API Gateway to Lambda via AWS_PROXY |
| `RoutePost` | `POST /links` — creates a short link |
| `RouteGet` | `GET /{id}` — redirects to the original URL |
| `LambdaPermission` | Allows API Gateway to invoke the Lambda |

## 🔧 Setup

### Prerequisites

- AWS account (free tier is enough)
- GitHub repository with the following secrets configured:

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | Target region (e.g. `us-east-2`) |
| `AWS_ACCOUNT_ID` | 12-digit AWS account ID |

### Deploy

Push to `main`. The GitHub Actions pipeline handles everything automatically.

After the first deploy, your frontend will be live at:

```
http://link-shortener-{AWS_ACCOUNT_ID}.s3-website.{AWS_REGION}.amazonaws.com
```

## 🧪 Running Tests Locally

```bash
pip install pytest boto3
pytest lambda/test_handler.py -v
```

Tests mock all DynamoDB calls — no AWS connection required.
