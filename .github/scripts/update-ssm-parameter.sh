#!/bin/bash
set -euo pipefail

# Script to update a key-value pair in an AWS SSM Parameter Store
# Usage: update-ssm-parameter.sh <parameter-name> <key> <value> <region>

if [ $# -ne 4 ]; then
    echo "Usage: $0 <parameter-name> <key> <value> <region>"
    echo "Example: $0 /workstations/2025.0.0 NUKE_TOOLS v1.2.3 eu-west-1"
    exit 1
fi

PARAMETER_NAME="$1"
KEY="$2"
VALUE="$3"
REGION="$4"

echo "Downloading parameter store: ${PARAMETER_NAME}"
# Download the current parameter store value
CONFIG=$(aws ssm get-parameter \
    --name "${PARAMETER_NAME}" \
    --region "${REGION}" \
    --query "Parameter.Value" \
    --output text)

echo "Updating ${KEY} to ${VALUE}"
# Update the key value with the new value
# If key exists, update it; otherwise append it
if echo "$CONFIG" | grep -q "^${KEY}="; then
    UPDATED_VALUE=$(echo "$CONFIG" | sed "s/^${KEY}=.*/${KEY}=${VALUE}/")
else
    UPDATED_VALUE="${CONFIG}"$'\n'"${KEY}=${VALUE}"
fi

echo "Uploading updated parameter store"
# Upload the updated parameter store back
aws ssm put-parameter \
    --name "${PARAMETER_NAME}" \
    --value "$UPDATED_VALUE" \
    --type "String" \
    --overwrite \
    --region "${REGION}"

echo "Successfully updated ${KEY} in ${PARAMETER_NAME}"
