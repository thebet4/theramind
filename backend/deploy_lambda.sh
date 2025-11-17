#!/bin/bash

set -e

if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    set -a
    source .env
    set +a
fi

FUNCTION_NAME="theramind-processor"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID="766715367087"
ROLE_NAME="theramind-processor-role"
RUNTIME="python3.11"
MEMORY_SIZE=1024
TIMEOUT=900

echo "🚀 TheraMind Worker - Complete Deployment"
echo "=========================================="
echo ""

echo "📋 Step 1: Using IAM Role..."
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo "✅ Using IAM role: ${ROLE_NAME}"
echo ""

# Skip role creation check to avoid permission issues
if false; then
    echo "📝 Creating IAM role..."
    
    cat > /tmp/trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    aws iam create-role \
        --role-name ${ROLE_NAME} \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "Execution role for TheraMind audio processor Lambda"

    echo "✅ IAM role created"
    
    aws iam attach-role-policy \
        --role-name ${ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    echo "✅ Attached basic Lambda execution policy"
    
    cat > /tmp/lambda-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::theramind-sessions/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ChangeMessageVisibility"
      ],
      "Resource": "arn:aws:sqs:${REGION}:${ACCOUNT_ID}:theramind-*"
    }
  ]
}
EOF

    aws iam put-role-policy \
        --role-name ${ROLE_NAME} \
        --policy-name theramind-processor-policy \
        --policy-document file:///tmp/lambda-policy.json
    
    echo "✅ Attached custom S3/SQS policy"
    
    echo "⏳ Waiting for IAM role to propagate (10 seconds)..."
    sleep 10
fi

echo ""

echo "📦 Step 2: Building deployment package..."
./build_lambda.sh

if [ ! -f lambda_function.zip ]; then
    echo "❌ Build failed - lambda_function.zip not found"
    exit 1
fi

echo ""

echo "🔍 Step 3: Checking Lambda function..."

if aws lambda get-function --function-name ${FUNCTION_NAME} --region ${REGION} 2>/dev/null; then
    echo "🔄 Function exists, updating code..."
    aws lambda update-function-code \
        --function-name ${FUNCTION_NAME} \
        --zip-file fileb://lambda_function.zip \
        --region ${REGION}
    
    echo "✅ Function code updated"
    
    echo "⚙️  Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name ${FUNCTION_NAME} \
        --timeout ${TIMEOUT} \
        --memory-size ${MEMORY_SIZE} \
        --region ${REGION} \
        > /dev/null
    
    echo "✅ Function configuration updated"
else
    echo "📝 Creating new Lambda function..."
    
    if [ -z "$DATABASE_URL" ] || [ -z "$OPENAI_API_KEY" ]; then
        echo ""
        echo "⚠️  WARNING: Required environment variables not set!"
        echo "Please set DATABASE_URL and OPENAI_API_KEY before creating the function."
        echo ""
        echo "Example:"
        echo "  export DATABASE_URL='postgresql://user:pass@host:5432/db'"
        echo "  export OPENAI_API_KEY='sk-proj-...'"
        echo ""
        echo "Or you can create the function without env vars and set them later in AWS Console."
        echo ""
        read -p "Continue without environment variables? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        ENV_VARS="Variables={S3_BUCKET_NAME=${S3_BUCKET_NAME:-theramind-sessions},AWS_REGION=${REGION},LOG_LEVEL=INFO}"
    else
        ENV_VARS="Variables={DATABASE_URL=$DATABASE_URL,OPENAI_API_KEY=$OPENAI_API_KEY,S3_BUCKET_NAME=${S3_BUCKET_NAME:-theramind-sessions},AWS_REGION=${REGION},LOG_LEVEL=INFO}"
    fi
    
    aws lambda create-function \
        --function-name ${FUNCTION_NAME} \
        --runtime ${RUNTIME} \
        --role ${ROLE_ARN} \
        --handler app.workers.lambda_handler.lambda_handler \
        --zip-file fileb://lambda_function.zip \
        --timeout ${TIMEOUT} \
        --memory-size ${MEMORY_SIZE} \
        --region ${REGION} \
        --environment "$ENV_VARS" \
        --description "TheraMind audio processing worker - transcribes, summarizes, and anonymizes therapy sessions"
    
    echo "✅ Lambda function created successfully!"
fi

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📌 Function Details:"
echo "   Name: ${FUNCTION_NAME}"
echo "   Region: ${REGION}"
echo "   ARN: arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}"
echo ""
echo "🔧 Next Steps:"
echo ""
echo "1. Set environment variables (if not already set):"
echo "   aws lambda update-function-configuration \\"
echo "     --function-name ${FUNCTION_NAME} \\"
echo "     --region ${REGION} \\"
echo "     --environment Variables='{DATABASE_URL=your_url,OPENAI_API_KEY=your_key,S3_BUCKET_NAME=theramind-sessions}'"
echo ""
echo "2. Configure SQS trigger:"
echo "   aws lambda create-event-source-mapping \\"
echo "     --function-name ${FUNCTION_NAME} \\"
echo "     --region ${REGION} \\"
echo "     --event-source-arn arn:aws:sqs:${REGION}:${ACCOUNT_ID}:theramind-jobs \\"
echo "     --batch-size 1"
echo ""
echo "3. View logs:"
echo "   aws logs tail /aws/lambda/${FUNCTION_NAME} --follow --region ${REGION}"
echo ""

