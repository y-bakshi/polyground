#!/bin/bash

# Integration test script
# Tests that backend API is working correctly with the database

set -e

echo "🧪 Integration Test Script"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backend URL
BACKEND_URL="http://localhost:8000"

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4

    echo -n "${BLUE}Testing:${NC} $description... "

    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL$endpoint")
    elif [ "$method" == "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BACKEND_URL$endpoint")
    fi

    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$status_code" == "200" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL (status: $status_code)${NC}"
        echo "  Response: $body"
        return 1
    fi
}

echo "${BLUE}Checking if backend is running...${NC}"
if ! curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend is not running at $BACKEND_URL${NC}"
    echo ""
    echo "Please start the backend first:"
    echo "  cd backend && source venv/bin/activate && uvicorn main:app --reload"
    echo ""
    echo "Or run both services:"
    echo "  ./start-dev.sh"
    exit 1
fi

echo -e "${GREEN}✓ Backend is running${NC}"
echo ""

# Run tests
echo "${BLUE}Running API endpoint tests...${NC}"
echo ""

test_endpoint "GET" "/health" "Health check"
test_endpoint "GET" "/" "Root endpoint"
test_endpoint "GET" "/api/pinned?userId=1" "Get pinned markets for user 1"
test_endpoint "GET" "/api/alerts?userId=1" "Get alerts for user 1"
test_endpoint "POST" "/api/pin" "Pin a market" '{"userId": 1, "marketId": "test-market-123"}'

echo ""
echo "${BLUE}Testing database data...${NC}"
echo ""

# Test that we have the test data
pinned_response=$(curl -s "$BACKEND_URL/api/pinned?userId=1")
pinned_count=$(echo "$pinned_response" | grep -o '"items"' | wc -l)

if [ "$pinned_count" -gt 0 ]; then
    echo -e "${GREEN}✓ Database has pinned markets${NC}"
else
    echo -e "${RED}✗ No pinned markets found${NC}"
fi

alerts_response=$(curl -s "$BACKEND_URL/api/alerts?userId=1")
alerts_count=$(echo "$alerts_response" | grep -o '"alerts"' | wc -l)

if [ "$alerts_count" -gt 0 ]; then
    echo -e "${GREEN}✓ Database has alerts${NC}"

    # Check if alerts have market_title
    if echo "$alerts_response" | grep -q "market_title"; then
        echo -e "${GREEN}✓ Alerts include market_title field${NC}"
    else
        echo -e "${RED}✗ Alerts missing market_title field${NC}"
    fi
else
    echo -e "${RED}✗ No alerts found${NC}"
fi

echo ""
echo "${GREEN}✅ Integration tests completed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start both services: ./start-dev.sh"
echo "  2. Open frontend: http://localhost:5173"
echo "  3. Check API docs: http://localhost:8000/docs"
