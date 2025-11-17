#!/bin/bash

set -e

echo "🔨 Building TheraMind Worker Lambda package..."

echo "🧹 Cleaning previous builds..."
if [ -d "lambda_package" ]; then
    docker run --rm --platform linux/amd64 --entrypoint /bin/rm -v "$PWD":/var/task public.ecr.aws/lambda/python:3.11 -rf /var/task/lambda_package
fi
rm -f lambda_function.zip

echo "📦 Creating package directory..."
mkdir -p lambda_package/

echo "🐳 Building dependencies using Docker (Lambda runtime environment)..."
docker run --rm \
  --platform linux/amd64 \
  --entrypoint /bin/bash \
  -v "$PWD":/var/task \
  public.ecr.aws/lambda/python:3.11 \
  -c "pip install -r requirements.txt -t /var/task/lambda_package/ --upgrade && chmod -R 755 /var/task/lambda_package/"

echo "📋 Copying application code..."
cp -r app lambda_package/

echo "🗜️  Creating ZIP file..."
cd lambda_package/
zip -r9 ../lambda_function.zip . -q
cd ..

PACKAGE_SIZE=$(du -h lambda_function.zip | cut -f1)
echo "✅ Build complete! Package size: $PACKAGE_SIZE"
echo ""
echo "📤 To deploy to Lambda, run:"
echo "./deploy_lambda.sh"

