"""
CDK Stack for NetworkEarth Shared S3 Bucket.

This stack creates a publicly readable S3 bucket for sharing research data
and publication materials. Write access is controlled via IAM (not public).
"""
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    RemovalPolicy,
)
from constructs import Construct


class NetworkEarthSharedStack(Stack):
    """
    CDK Stack that creates a publicly readable S3 bucket.

    The bucket allows public HTTPS access for GET and LIST operations,
    while write access remains controlled through IAM policies.

    Attributes:
        bucket: The S3 bucket resource for shared data
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initialize the NetworkEarth Shared S3 bucket stack.

        Args:
            scope: The scope in which this stack is defined
            construct_id: The scoped construct ID
            **kwargs: Additional stack properties including environment
        """
        super().__init__(scope, construct_id, **kwargs)

        # Create the S3 bucket with public read access
        self.bucket = s3.Bucket(
            self,
            "NetworkEarthSharedBucket",
            bucket_name="networkearth-shared",
            # Allow public read access via HTTPS
            public_read_access=True,
            # Block public ACLs but allow public bucket policies
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=False,  # Allow public policy for reads
                ignore_public_acls=True,
                restrict_public_buckets=False,  # Allow public access
            ),
            # Enforce HTTPS only
            enforce_ssl=True,
            # Keep all data indefinitely (no lifecycle rules)
            lifecycle_rules=[],
            # Retain bucket if stack is deleted (data safety)
            removal_policy=RemovalPolicy.RETAIN,
            # Enable versioning for data protection
            versioned=False,  # Not specified in requirements, defaulting to False
            # Disable automatic object deletion on stack removal
            auto_delete_objects=False,
        )

        # Add explicit bucket policy for public read access via HTTPS
        self.bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="PublicReadGetObject",
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=[
                    "s3:GetObject",
                    "s3:ListBucket",
                ],
                resources=[
                    self.bucket.bucket_arn,
                    f"{self.bucket.bucket_arn}/*",
                ],
                conditions={
                    "Bool": {
                        "aws:SecureTransport": "true"
                    }
                }
            )
        )
