# 🐛 Debug Mode Documentation

## Overview

Debug mode provides comprehensive logging and debugging output for the NSE Stock Analysis app. It tracks all operations across the multi-agent system and writes detailed logs to a file and console.

## Enabling Debug Mode

Debug mode is **enabled by default**. To disable it, edit `config.py`:

```python
DEBUG_MODE = False  # Change from True to False
```

## Configuration Options

In `config.py`:

```python
# Debug Configuration
DEBUG_MODE = True              # Enable/disable debug mode
DEBUG_VERBOSE = True           # Verbose output (extra details)
DEBUG_LOG_FILE = "debug.log"  # Log file location
LOG_LEVEL = "DEBUG"            # Logging level
```

## Log Output Locations

### 1. Log File
- **Location**: `debug.log` in the project root
- **Format**: Includes timestamps, function names, line numbers
- **Persistence**: Appended across sessions (useful for tracking issues)

### 2. Console Output
- **Display**: Real-time output in terminal
- **Format**: Same as log file

## Log Format

```
2026-05-02 14:15:23,456 - __main__ - DEBUG - [run_analysis:245] - Analysis started at: 2026-05-02T14:15:23.456789
```

Components:
- **Timestamp**: `2026-05-02 14:15:23,456`
- **Logger**: `__main__`
- **Level**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Location**: `[function_name:line_number]`
- **Message**: Actual log message

## What Gets Logged

### Application Lifecycle
```
✓ App startup
✓ Debug mode enabled/disabled
✓ Configuration loaded
✓ Session state initialized
```

### Analysis Pipeline
```
✓ Stock ticker analysis started
✓ Each agent initialization
✓ Data fetching progress
✓ Analysis calculations
✓ Final recommendation
✓ Session state updates
```

### Stock Scraper Agent
```
✓ Ticker formatting
✓ Data fetch requests
✓ API calls to Yahoo Finance
✓ Data validation
✓ Error handling
```

### News Scraper Agent
```
✓ News fetch requests
✓ Articles retrieved
✓ Sentiment analysis results
```

### Analysis Agent
```
✓ Technical indicator calculations
✓ Number of data points processed
✓ Fundamental metrics
✓ Trend analysis
✓ Score calculations
```

### CEO Agent
```
✓ Orchestration start
✓ Data synthesis
✓ Recommendation generation
✓ Report generation completion
```

## Using the Logs

### View Live Logs
While the app is running, check the console output in your terminal for real-time logs.

### View Log File
After analysis, inspect the log file:

```bash
# View entire log
cat debug.log

# View last 50 lines
tail -50 debug.log

# Search for errors
grep -i "error" debug.log

# Search for specific ticker
grep "RELIANCE" debug.log

# Follow logs in real-time (macOS/Linux)
tail -f debug.log
```

### Clear Logs
To start fresh:

```bash
rm debug.log
```

## Common Log Patterns

### Successful Analysis
```
INFO - NSE Stock Analysis App Started
DEBUG - DEBUG MODE ENABLED
DEBUG - StockScraperAgent initialized in DEBUG mode
INFO - Step 1: Initializing StockScraperAgent
INFO - Fetching stock data for RELIANCE
DEBUG - Stock data fetched successfully: 15 keys
INFO - Step 2: Initializing NewsScraperAgent
INFO - Fetching news for Reliance Industries
DEBUG - News fetched: 20 articles
INFO - Step 3: Initializing AnalysisAgent
DEBUG - AnalysisAgent created with 200 data points
INFO - Performing technical analysis...
DEBUG - Technical analysis complete: 18 indicators
INFO - Performing fundamental analysis...
DEBUG - Fundamental analysis complete: 7 metrics
INFO - Calculating combined score...
INFO - Combined score calculated: 65/100
INFO - Step 4: Initializing CEOAgent
INFO - Orchestrating all agent data...
DEBUG - Final report generated with recommendation: BUY
INFO - Analysis successfully completed for RELIANCE
```

### Error in Analysis
```
ERROR - Failed to fetch stock data: No data found for INVALID_TICKER.NS
```

## Debugging Tips

### 1. Check Agent Initialization
Look for lines like:
```
DEBUG - StockScraperAgent initialized in DEBUG mode
DEBUG - AnalysisAgent initialized in DEBUG mode
```

If missing, agents may not be initializing properly.

### 2. Track Data Flow
Follow the data through each step:
```
INFO - Step 1: Fetching stock data
DEBUG - Stock data fetched successfully: 15 keys
INFO - Step 2: Gathering market news
DEBUG - News fetched: 20 articles
```

### 3. Monitor Calculations
Check indicator calculations:
```
DEBUG - Technical analysis complete: 18 indicators
DEBUG - Score breakdown - Technical signals processed
```

### 4. Verify Recommendations
Confirm the final recommendation:
```
INFO - Combined score calculated: 65/100
DEBUG - Final report generated with recommendation: BUY
```

## Log Levels Explained

| Level | Purpose | Example |
|-------|---------|---------|
| DEBUG | Detailed diagnostic information | Function calls, data counts, calculations |
| INFO | Confirmation of expected behavior | "Analysis started", "Data fetched" |
| WARNING | Warning about potential issues | Deprecated functions, missing optional data |
| ERROR | Error that occurred | "Failed to fetch data", "Invalid ticker" |
| CRITICAL | Serious error, program may stop | Out of memory, system errors |

## Performance Debugging

### Check Analysis Duration
Look for timing information in logs:
```
INFO - Analysis started at: 2026-05-02T14:15:23
INFO - Analysis successfully completed at: 2026-05-02T14:15:38
```

Difference = ~15 seconds (normal for first run)

### Identify Bottlenecks
Each agent logs when it completes:
```
INFO - Step 1: Fetching stock data... (usually 2-3 seconds)
INFO - Step 2: Gathering market news... (usually 1-2 seconds)
INFO - Step 3: Performing analysis... (usually 2-3 seconds)
INFO - Step 4: Generating report... (usually 1-2 seconds)
```

If any step takes significantly longer, that's the bottleneck.

## Disabling Debug Mode for Production

To reduce log verbosity in production:

```python
# config.py
DEBUG_MODE = False
LOG_LEVEL = "INFO"
```

This will:
- Only log important information
- Reduce log file size
- Slightly improve performance
- Remove function/line number info

## Advanced Usage

### Custom Log Filtering

Find all operations for a specific ticker:
```bash
grep "RELIANCE\|TCS" debug.log
```

Find all errors and warnings:
```bash
grep -E "ERROR|WARNING" debug.log
```

Find slow operations (>5 seconds):
```bash
grep "analysis\|fetch" debug.log | tail -20
```

### Log Analysis Workflow

1. **Run analysis with debug enabled**
2. **Check for errors**: `grep ERROR debug.log`
3. **Review timing**: Look at timestamps
4. **Verify calculations**: Check indicator values
5. **Confirm recommendation**: Check final recommendation score

## Troubleshooting with Logs

### Issue: "No data found"
Check logs for:
```
Ticker formatting messages
API error messages
Data validation failures
```

### Issue: Slow Analysis
Check logs for:
```
Times between each step
Number of data points processed
API response times
```

### Issue: Wrong Recommendation
Check logs for:
```
Score calculation logs
Technical indicator values
Fundamental metric values
Weighting calculations
```

## Best Practices

✅ **Do:**
- Keep debug mode ON during development
- Review logs after analysis completes
- Check logs when analysis fails
- Search logs for specific information
- Archive logs for troubleshooting

❌ **Don't:**
- Leave debug mode ON in production (if concerned about performance)
- Ignore error messages in logs
- Manually edit log files
- Assume everything is fine without checking logs

## Example Debugging Session

```bash
# 1. Start app with debug enabled
bash quickstart.sh

# 2. Run analysis in the UI for RELIANCE

# 3. In another terminal, check logs
tail -50 debug.log

# 4. Search for any errors
grep ERROR debug.log

# 5. Review the full analysis flow
grep "Step\|completed\|recommendation" debug.log

# 6. Check timing
grep "started\|complete" debug.log | head -20
```

## Need Help?

If analysis fails:
1. Enable debug mode
2. Run analysis again
3. Check `debug.log` for error messages
4. Search for the specific error
5. Review the sequence of logs leading to the error

---

**Debug mode makes troubleshooting easier and faster!** 🐛✨
