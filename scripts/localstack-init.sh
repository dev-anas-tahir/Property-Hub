#!/bin/bash

echo "🚀 Initializing LocalStack S3 buckets..."

# Create buckets if they don't exist
awslocal s3 ls s3://propertyhub-media 2>/dev/null || awslocal s3 mb s3://propertyhub-media
awslocal s3 ls s3://propertyhub-static 2>/dev/null || awslocal s3 mb s3://propertyhub-static

# Set bucket policies to allow public read access
awslocal s3api put-bucket-acl --bucket propertyhub-media --acl public-read
awslocal s3api put-bucket-acl --bucket propertyhub-static --acl public-read

# Configure CORS for the buckets
awslocal s3api put-bucket-cors --bucket propertyhub-media --cors-configuration '{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"]
    }
  ]
}'

awslocal s3api put-bucket-cors --bucket propertyhub-static --cors-configuration '{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"]
    }
  ]
}'

echo "✅ S3 buckets created and configured:"
echo "   - propertyhub-media (for user uploads)"
echo "   - propertyhub-static (for static files)"
