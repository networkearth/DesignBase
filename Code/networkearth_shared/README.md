# NetworkEarth Shared S3 Bucket

A CDK project to deploy a publicly readable S3 bucket for sharing NetworkEarth research data and publication materials.

## Overview

This CDK application creates an S3 bucket named `networkearth-shared` in AWS account `575101084097` (us-east-1 region). The bucket is configured to:

- Allow public read access via HTTPS for GET and LIST operations
- Enforce SSL/TLS for all connections
- Restrict write access through IAM policies (not publicly writable)
- Retain all data indefinitely (no lifecycle expiration)

## Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate credentials
- AWS CDK v2.x installed (`npm install -g aws-cdk`)
- Access to AWS account `575101084097`
- Account must be CDK bootstrapped in us-east-1 region (already done per design)

## Installation

1. Navigate to the project directory:
   ```bash
   cd Code/networkearth_shared
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Deployment

### Deploy the Stack

To deploy the S3 bucket to AWS:

```bash
cdk deploy
```

This will:
1. Synthesize the CloudFormation template
2. Show you the changes to be made
3. Ask for confirmation before deploying
4. Create the `networkearth-shared` S3 bucket with public read access

### View the Synthesized CloudFormation Template

To see the CloudFormation template without deploying:

```bash
cdk synth
```

### Verify the Deployment

After deployment, you can verify the bucket exists:

```bash
aws s3 ls s3://networkearth-shared/ --region us-east-1
```

## Usage

### Uploading Data (Requires IAM Permissions)

To upload files to the bucket, you need appropriate IAM write permissions:

```bash
aws s3 cp myfile.csv s3://networkearth-shared/path/to/myfile.csv
```

### Public Access (Read-Only)

Anyone can access objects via HTTPS:

```
https://networkearth-shared.s3.amazonaws.com/path/to/myfile.csv
```

Or via AWS CLI:

```bash
aws s3 cp s3://networkearth-shared/path/to/myfile.csv ./local-copy.csv --no-sign-request
```

### List Bucket Contents (Public)

Anyone can list the bucket contents:

```bash
aws s3 ls s3://networkearth-shared/ --no-sign-request
```

## Architecture

### Stack Components

- **S3 Bucket**: `networkearth-shared`
  - Public read access via HTTPS
  - SSL enforced
  - No automatic deletion
  - Retained on stack deletion

### Security

- Write access is NOT public and must be granted via IAM policies
- All access must use HTTPS (SSL/TLS enforced)
- Public ACLs are blocked, but bucket policy allows public reads

## Maintenance

### Update the Stack

After making changes to `stack.py` or `app.py`:

```bash
cdk diff    # View changes
cdk deploy  # Apply changes
```

### Destroy the Stack

To remove the CloudFormation stack (note: bucket will be retained due to RemovalPolicy.RETAIN):

```bash
cdk destroy
```

The S3 bucket itself will not be deleted automatically to protect data.

## Troubleshooting

### Permission Denied

Ensure your AWS credentials have permission to create S3 buckets and modify bucket policies in account `575101084097`.

### Bucket Already Exists

If the bucket name is already taken, you may need to either:
1. Delete the existing bucket (if you own it)
2. Change the bucket name in `stack.py`

### CDK Bootstrap Required

If you see errors about missing CDK bootstrap resources:

```bash
cdk bootstrap aws://575101084097/us-east-1
```

(This should already be done per the design specifications)

## Project Structure

```
networkearth_shared/
├── app.py              # CDK application entry point
├── stack.py            # Stack definition with S3 bucket
├── cdk.json           # CDK configuration
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Design Specifications

This implementation follows the design specifications in:
`Design/Publishing/Data/Bucket.md`

Key requirements met:
- Bucket name: `networkearth-shared`
- Public read access via HTTPS (GET and LIST)
- Private write access (IAM controlled)
- Account: `575101084097`
- Region: `us-east-1`
- Deployment: `cdk deploy`
- Data retention: indefinite (no lifecycle rules)
