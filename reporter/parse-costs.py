import os
import sys
import requests
import json
import csv
import traceback
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PERFORMANCE_API_BASEPATH = "http://qacdco.hi.inet/pre-performance/reporter/api/1.0/"

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

API_VERSION = "2021-10-01"
REQUEST_URL_TEMPLATE = "https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version={api_version}&$top=5000"

enabled_projects = {
    "16": "f0d97868-f735-4c2c-b386-31a0f9c225c2",
}

def get_access_token(tenant_id, client_id, client_secret):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://management.azure.com/.default"
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

def get_costs(subscription_id, start_date, end_date, token):
    body = {
        "type": "ActualCost",
        "dataSet": {
            "granularity": "None",
            "aggregation": {
                "totalCost": {
                    "name": "Cost",
                    "function": "Sum"
                },
                "totalCostUSD": {
                    "name": "CostUSD",
                    "function": "Sum"
                }
            },
            "grouping": [
                {"type": "Dimension", "name": "ResourceId"},
                {"type": "Dimension", "name": "ResourceType"},
                {"type": "Dimension", "name": "ResourceLocation"},
                {"type": "Dimension", "name": "ChargeType"},
                {"type": "Dimension", "name": "ResourceGroupName"},
                {"type": "Dimension", "name": "PublisherType"},
                {"type": "Dimension", "name": "ServiceName"},
                {"type": "Dimension", "name": "ServiceTier"},
                {"type": "Dimension", "name": "Meter"}
            ],
            "include": ["Tags"]
        },
        "timeframe": "Custom",
        "timePeriod": {
            "from": start_date,
            "to": end_date
        }
    }

    url = REQUEST_URL_TEMPLATE.format(subscription_id=subscription_id, api_version=API_VERSION)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()

def patch_execution_cost(execution_id, cost):
    cost_str = f"{cost:.2f}"
    logger.debug(f"Updating test_cost={cost_str} for execution_id={execution_id} in the internal API.")
    url = PERFORMANCE_API_BASEPATH + f"executions/{execution_id}/"
    payload = {'test_cost': cost_str}
    try:
        response = requests.patch(url, json=payload)
        if response.status_code not in [200, 204]:
            logger.error(f"Error updating cost for execution_id={execution_id}. "
                         f"Status: {response.status_code}, Response: {response.text}")
        else:
            logger.info(f"Execution {execution_id} updated with cost={cost_str}")
    except Exception as e:
        logger.error(f"Exception while PATCHing execution_id={execution_id}: {e}")
        logger.debug(traceback.format_exc())

def patch_project_cost(project_id, cost):
    cost_str = f"{cost:.2f}"
    logger.debug(f"Updating cost={cost_str} for project_id={project_id} in the internal API.")
    url = PERFORMANCE_API_BASEPATH + f"projects/{project_id}/"
    payload = {'cost': cost_str}
    try:
        response = requests.patch(url, json=payload)
        if response.status_code not in [200, 204]:
            logger.error(f"Error updating cost for project_id={project_id}. "
                         f"Status: {response.status_code}, Response: {response.text}")
        else:
            logger.info(f"Project {project_id} updated with cost={cost_str}")
    except Exception as e:
        logger.error(f"Exception while PATCHing project_id={project_id}: {e}")
        logger.debug(traceback.format_exc())

def main(days_ago):
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("Please set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET environment variables.")
        sys.exit(1)

    token = get_access_token(TENANT_ID, CLIENT_ID, CLIENT_SECRET)

    now = datetime.utcnow()

    start = (now - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
    start_date_tags = start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    end_date_tags = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    logger.info(f"Fetching costs for tags from {start_date_tags} to {end_date_tags}")

    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date_month = month_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    end_date_month = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    logger.info(f"Fetching monthly project costs from {start_date_month} to {end_date_month}")

    aggregated_costs = {}
    execution_costs = {}
    
    for project, subscription_id in enabled_projects.items():
        result = get_costs(subscription_id, start_date_tags, end_date_tags, token)
        for item in result.get("properties", {}).get("rows", []):
            cost = float(item[0])
            tags = item[-2] if isinstance(item[-2], list) else []
            if not tags:
                continue
            for tag in tags:
                key, value = tag.replace('"', '').split(':', 1)
                if key.strip() != 'reporterid':
                    continue
                execution_id = value.strip()
                cleaned_tag = f"{key.strip()}:{execution_id}"
                if cleaned_tag not in aggregated_costs:
                    aggregated_costs[cleaned_tag] = {}
                if project not in aggregated_costs[cleaned_tag]:
                    aggregated_costs[cleaned_tag][project] = 0.0
                aggregated_costs[cleaned_tag][project] += cost

                if execution_id not in execution_costs:
                    execution_costs[execution_id] = 0.0
                execution_costs[execution_id] += cost


    for execution_id, total_cost in execution_costs.items():
        patch_execution_cost(execution_id, total_cost)

    for project, subscription_id in enabled_projects.items():
        monthly_result = get_costs(subscription_id, start_date_month, end_date_month, token)
        total_monthly_cost = 0.0
        for item in monthly_result.get("properties", {}).get("rows", []):
            cost = float(item[0])
            total_monthly_cost += cost
        patch_project_cost(project, total_monthly_cost)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse-costs.py <DAYS_AGO>")
        print("Example: python parse-costs.py 30")
        sys.exit(1)

    days_ago = int(sys.argv[1])
    main(days_ago)
