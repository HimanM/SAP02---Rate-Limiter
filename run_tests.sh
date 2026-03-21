#!/usr/bin/env bash

# ANSI color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "\n${CYAN}====================================================${NC}"
echo -e "${CYAN}        Active Distributed Container Stack        ${NC}"
echo -e "${CYAN}====================================================${NC}"
docker compose ps

echo -e "\n${GREEN}» Initiating Telemetry: Burst Capacity Validation...${NC}"
python tests/burst_test.py

echo -e "\n${GREEN}» Initiating Telemetry: NGINX Dynamic Load Balancing Validation...${NC}"
python tests/load_balance_test.py
