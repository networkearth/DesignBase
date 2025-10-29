#!/usr/bin/env python3
"""
CDK Application Entry Point for NetworkEarth Shared S3 Bucket.

This application deploys a publicly readable S3 bucket for sharing research data
and publication materials.
"""
import aws_cdk as cdk
from stack import NetworkEarthSharedStack


app = cdk.App()

NetworkEarthSharedStack(
    app,
    "NetworkEarthSharedStack",
    env=cdk.Environment(
        account="575101084097",
        region="us-east-1"
    ),
    description="Public S3 bucket for sharing NetworkEarth research data and publications"
)

app.synth()
