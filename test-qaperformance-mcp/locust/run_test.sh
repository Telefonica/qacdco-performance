#!/bin/bash

###############################################################################
# Locust Performance Test Runner
#
# This script executes Locust performance tests against the QA Performance API
# and collects CSV results in JMeter format.
#
# Usage:
#   ./run_test.sh [OPTIONS]
#
# Options:
#   -u, --users NUM        Number of concurrent users (default: 10)
#   -r, --ramp-up NUM      Spawn rate - users per second (default: 2)
#   -t, --time DURATION    Test duration in seconds (default: 60)
#   -h, --help             Show this help message
#
# Examples:
#   ./run_test.sh -u 50 -r 5 -t 120
#   ./run_test.sh --users 100 --ramp-up 10 --time 300
###############################################################################

set -e  # Exit on error

# Default values
USERS=10
RAMP_UP=2
DURATION=60
HOST="http://qacdco.hi.inet"
LOCUST_FILE="locustfile.py"
LOCUST_PORT=8089

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="$RESULTS_DIR/locust_results_${TIMESTAMP}.csv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Help function
show_help() {
    sed -n '/^###############################################################################/,/^###############################################################################/p' "$0" | grep -v "^###" | sed 's/^# //'
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--users)
            USERS="$2"
            shift 2
            ;;
        -r|--ramp-up)
            RAMP_UP="$2"
            shift 2
            ;;
        -t|--time)
            DURATION="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Validate parameters
if ! [[ "$USERS" =~ ^[0-9]+$ ]] || [ "$USERS" -lt 1 ]; then
    echo -e "${RED}Error: Users must be a positive integer${NC}"
    exit 1
fi

if ! [[ "$RAMP_UP" =~ ^[0-9]+$ ]] || [ "$RAMP_UP" -lt 1 ]; then
    echo -e "${RED}Error: Ramp-up must be a positive integer${NC}"
    exit 1
fi

if ! [[ "$DURATION" =~ ^[0-9]+$ ]] || [ "$DURATION" -lt 1 ]; then
    echo -e "${RED}Error: Duration must be a positive integer${NC}"
    exit 1
fi

# Create results directory if it doesn't exist
mkdir -p "$RESULTS_DIR"

# Print test configuration
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Locust Performance Test Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Host:${NC}            $HOST"
echo -e "${GREEN}Locustfile:${NC}      $LOCUST_FILE"
echo -e "${GREEN}Users:${NC}           $USERS"
echo -e "${GREEN}Ramp-up rate:${NC}    $RAMP_UP users/sec"
echo -e "${GREEN}Duration:${NC}        $DURATION seconds"
echo -e "${GREEN}Results file:${NC}    $RESULTS_FILE"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Locust web UI is accessible
echo -e "${YELLOW}Checking if Locust is running on localhost:${LOCUST_PORT}...${NC}"
if ! curl -s "http://localhost:${LOCUST_PORT}/" > /dev/null 2>&1; then
    echo -e "${RED}Error: Locust web UI is not accessible at http://localhost:${LOCUST_PORT}${NC}"
    echo -e "${RED}Please start Locust first with: locust -f $LOCUST_FILE --host=$HOST${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Locust is running${NC}"
echo ""

# Start test via API
echo -e "${GREEN}Starting Locust test via API...${NC}"
START_TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
START_EPOCH=$(date +%s)
echo -e "${BLUE}Start time:${NC}        $START_TIMESTAMP"
echo -e "${BLUE}Start timestamp:${NC}   $START_EPOCH"
echo ""

# Start the swarm
SWARM_RESPONSE=$(curl -s -X POST "http://localhost:${LOCUST_PORT}/swarm" \
    -d "user_count=${USERS}" \
    -d "spawn_rate=${RAMP_UP}" \
    -H "Content-Type: application/x-www-form-urlencoded")

if [[ $SWARM_RESPONSE == *"success"* ]] || [[ $SWARM_RESPONSE == *"Swarming"* ]]; then
    echo -e "${GREEN}✓ Test started successfully${NC}"
else
    echo -e "${YELLOW}Warning: Unexpected response when starting test${NC}"
fi

echo -e "${YELLOW}Test is running for ${DURATION} seconds...${NC}"

# Monitor test progress
ELAPSED=0
INTERVAL=10

while [ $ELAPSED -lt $DURATION ]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))

    if [ $ELAPSED -le $DURATION ]; then
        REMAINING=$((DURATION - ELAPSED))
        echo -e "${BLUE}Test progress: ${ELAPSED}s / ${DURATION}s (${REMAINING}s remaining)${NC}"
    fi
done

# Stop the test
echo -e "${YELLOW}Stopping test...${NC}"
curl -s -X GET "http://localhost:${LOCUST_PORT}/stop" > /dev/null 2>&1

LOCUST_EXIT_CODE=0

END_TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
END_EPOCH=$(date +%s)
ACTUAL_DURATION=$((END_EPOCH - START_EPOCH))

echo ""
echo -e "${GREEN}Test completed!${NC}"
echo -e "${BLUE}End time:${NC}          $END_TIMESTAMP"
echo -e "${BLUE}End timestamp:${NC}     $END_EPOCH"
echo -e "${BLUE}Total duration:${NC}    ${ACTUAL_DURATION}s"
echo ""

# Download CSV results from Locust web endpoint (JMeter format)
echo -e "${YELLOW}Downloading CSV results (JMeter format)...${NC}"

# Wait a moment for Locust to process final stats
sleep 3

# Download JMeter format CSV from custom endpoint
if curl -s "http://localhost:${LOCUST_PORT}/csv_results.csv" -o "$RESULTS_FILE" 2>/dev/null; then
    if [ -s "$RESULTS_FILE" ]; then
        echo -e "${GREEN}✓ CSV results saved to: $RESULTS_FILE${NC}"

        # Count number of results (excluding header)
        RESULT_COUNT=$(($(wc -l < "$RESULTS_FILE") - 1))
        echo -e "${GREEN}✓ Total requests recorded: $RESULT_COUNT${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: CSV file is empty${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Warning: Could not download CSV results from Locust web endpoint${NC}"
fi

# Print summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Results Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Start time:${NC}        $START_TIMESTAMP (Unix: $START_EPOCH)"
echo -e "${GREEN}End time:${NC}          $END_TIMESTAMP (Unix: $END_EPOCH)"
echo -e "${GREEN}Planned duration:${NC}  $DURATION seconds"
echo -e "${GREEN}Actual duration:${NC}   ${ACTUAL_DURATION} seconds"

if [ -f "$RESULTS_FILE" ] && [ -s "$RESULTS_FILE" ]; then
    echo -e "${GREEN}CSV results:${NC}     $RESULTS_FILE"

    # Count number of results
    RESULT_COUNT=$(($(wc -l < "$RESULTS_FILE") - 1))
    echo -e "${GREEN}Total requests:${NC}  $RESULT_COUNT"
fi

echo -e "${BLUE}========================================${NC}"

# Exit with Locust's exit code
exit $LOCUST_EXIT_CODE
