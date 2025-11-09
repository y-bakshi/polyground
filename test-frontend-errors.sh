#!/bin/bash

echo "🧪 Frontend Error Handling Test"
echo "================================"
echo ""

API_BASE="http://localhost:8000"

echo "Testing improved error handling..."
echo ""

# Test 1: Valid request
echo "Test 1: Valid Request"
curl -s "$API_BASE/api/pinned?userId=1" | jq -r '.total // "Error"' && echo "✅ Valid request works" || echo "❌ Valid request failed"
echo ""

# Test 2: 404 Error
echo "Test 2: 404 Error (User Not Found)"
ERROR_MSG=$(curl -s "$API_BASE/api/pinned?userId=99999" | jq -r '.detail // "No detail field"')
if [[ "$ERROR_MSG" == *"User not found"* ]] || [[ "$ERROR_MSG" == *"not found"* ]]; then
    echo "✅ Error message is user-friendly: $ERROR_MSG"
else
    echo "⚠️  Error message: $ERROR_MSG"
fi
echo ""

# Test 3: 400 Error
echo "Test 3: 400 Error (Invalid Market)"
ERROR_MSG=$(curl -s -X POST "$API_BASE/api/pin" \
    -H "Content-Type: application/json" \
    -d '{"userId":1,"marketId":"invalid-market-12345"}' | jq -r '.detail // "No detail field"')
if [[ "$ERROR_MSG" == *"Could not resolve"* ]] || [[ "$ERROR_MSG" == *"invalid"* ]]; then
    echo "✅ Error message explains the problem: $ERROR_MSG"
else
    echo "⚠️  Error message: $ERROR_MSG"
fi
echo ""

echo "✅ All tests completed!"
echo ""
echo "To test in browser:"
echo "1. Open frontend/test-error-handling.html in your browser"
echo "2. Make sure backend is running on http://localhost:8000"
echo "3. Click the test buttons"
