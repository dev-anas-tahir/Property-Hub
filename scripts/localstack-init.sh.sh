#!/bin/bash
awslocal s3 mb s3://propertyhub-media
awslocal s3 mb s3://propertyhub-static
echo "✅ S3 buckets created"
