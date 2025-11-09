# Testing Guide

This guide covers testing the Polymarket Analytics application.

## Quick Test

### Integration Test Script

Run the automated integration test:

```bash
./test-integration.sh
```

This tests all API endpoints and verifies the integration between frontend and backend.

## Frontend Testing

### Error Handling Tests

The frontend has improved error handling. Test it using:

#### Method 1: HTML Test Page

1. Start the backend:
   ```bash
   cd backend && source venv/bin/activate
   uvicorn main:app --reload
   ```

2. Open `frontend/test-error-handling.html` in your browser

3. Click each test button to verify error handling

#### Method 2: Browser DevTools

1. Start both services:
   ```bash
   ./start-dev.sh
   ```

2. Open http://localhost:5173 in browser

3. Open DevTools (F12) → Console tab

4. Test error scenarios:
   - Try to pin invalid market ID
   - Try to fetch data for non-existent user
   - Stop backend and try a request

#### Method 3: Command Line

```bash
./test-frontend-errors.sh
```

### Frontend Test Scenarios

#### ✅ Valid Request
- Make a valid API call
- Verify data loads correctly
- No errors in console

#### ✅ 404 Error (User Not Found)
- Request with invalid user ID (e.g., 99999)
- Check console for error message
- **Expected:** "User not found" (not raw response)

#### ✅ 400 Error (Bad Request)
- Try to pin invalid market ID
- Check console for error message
- **Expected:** "Could not resolve 'invalid-id' to a valid market or event"

#### ✅ 500 Error (Server Error)
- Cause a server error (e.g., database issue)
- Check console for error message
- **Expected:** User-friendly error message

#### ✅ Network Error
- Stop backend server
- Make an API call
- Check console for error
- **Expected:** Meaningful error message or fallback to mock data

## Backend Testing

### API Endpoint Tests

#### Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

#### Pin Market
```bash
curl -X POST http://localhost:8000/api/pin \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "marketId": "516710"}'
```

#### Get Pinned Markets
```bash
curl http://localhost:8000/api/pinned?userId=1
```

#### Get Market Details
```bash
curl http://localhost:8000/api/market/516710?hours=24
```

#### Get Alerts
```bash
curl http://localhost:8000/api/alerts?userId=1
```

### Database Tests

#### Test Database Initialization
```bash
cd backend
source venv/bin/activate
python init_db.py --seed
```

#### Verify Tables Created
```bash
python -c "
from database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"
```

### Worker Tests

#### Verify Worker is Running
Check backend logs:
```bash
tail -f backend.log | grep worker
```

You should see:
```
INFO - Starting market polling worker...
INFO - Polling 7 pinned markets
```

#### Test Alert Generation
1. Pin a market with active trading
2. Wait for polling interval (default: 300 seconds)
3. Check if alerts are created when threshold is exceeded

## Integration Testing

### Full User Flow Test

1. **Start both services:**
   ```bash
   ./start-dev.sh
   ```

2. **Pin a market:**
   - Open http://localhost:5173
   - Enter a Polymarket market ID or URL
   - Click "Pin Market"

3. **Verify data appears:**
   - Market should appear in pinned markets table
   - Data should refresh every 60 seconds

4. **Check alerts:**
   - Navigate to Alerts page
   - Wait for worker to detect changes
   - Verify alerts appear with insights

### Test Results

See `TEST_RESULTS.md` for detailed test results from the improvements implementation.

**Summary:**
- ✅ 28 tests run
- ✅ 27 passed (96% pass rate)
- ✅ 0 failures
- ⚠️ 1 expected issue (database index - needs table recreation)

## Test Checklist

### Backend Testing
- [ ] All endpoints respond correctly
- [ ] Error handling works (404, 400, 500)
- [ ] Database operations succeed
- [ ] Worker polls markets correctly
- [ ] Alerts are generated when thresholds are met
- [ ] Claude insights are generated
- [ ] CORS is configured correctly

### Frontend Testing
- [ ] API calls work correctly
- [ ] Error messages are user-friendly
- [ ] Data refreshes automatically
- [ ] Mock data fallback works
- [ ] UI displays data correctly
- [ ] No console errors

### Integration Testing
- [ ] Frontend connects to backend
- [ ] Data flows correctly
- [ ] Real-time updates work
- [ ] Alerts appear in frontend
- [ ] Market pinning works end-to-end

## Troubleshooting Tests

### Tests Fail to Connect

**Problem:** Cannot connect to backend
**Solution:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check `VITE_API_BASE_URL` in frontend `.env`
- Check CORS configuration

### Mock Data Always Shows

**Problem:** Frontend always uses mock data
**Solution:**
- Set `VITE_USE_MOCK=false` in frontend `.env`
- Verify backend is responding
- Check browser console for errors

### Worker Not Polling

**Problem:** No market data being collected
**Solution:**
- Check `ENABLE_WORKER=true` in backend `.env`
- Verify markets are pinned
- Check backend logs for errors

## Performance Testing

### Load Testing

Test API performance with multiple requests:

```bash
# Test with Apache Bench
ab -n 100 -c 10 http://localhost:8000/api/pinned?userId=1

# Test with curl in loop
for i in {1..10}; do
  curl http://localhost:8000/api/pinned?userId=1 &
done
wait
```

### Database Performance

Test query performance:
```bash
# Time a query
time curl http://localhost:8000/api/pinned?userId=1
```

## Automated Testing

### Integration Test Script

The `test-integration.sh` script tests:
- Health endpoint
- Pin/unpin operations
- Market data retrieval
- Alert retrieval
- Error handling

Run it:
```bash
./test-integration.sh
```

## Next Steps

After testing, see:
- [Running Guide](running.md) - How to run the application
- [Documentation](documentation.md) - API documentation and architecture

