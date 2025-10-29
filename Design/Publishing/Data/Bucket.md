## Purpose

To have an s3 bucket that can be used to make data available to others (especially for publishing papers). 

## Requirements

- **name**: `networkearth-shared`
- **policy**:
  - Open to the public for reading (https) (for get or list)
  - Not public for write access (controlled by IAM) (will be dealt with elsewhere)
- **account**: `575101084097`
- **region**: `us-east-1`
- **deployment**: through `cdk deploy`
- **lifecycle**: all data should be held there indefinitely

## Notes

The account/region is already CDK bootstrapped.

## Structure

```bash
networkearth_shared/
+-- cdk.json
+-- app.py
+-- stack.py
```

## Dependencies
- AWS CDK v2.x
- Python 3.9+
- AWS CLI configured with credentials
- Required Python packages: aws-cdk-lib, constructs