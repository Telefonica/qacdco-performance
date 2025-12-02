import logging
import uuid

from locust import HttpUser, task, constant_pacing, events
from common.hooks import JmeterListener


class ListProjectsUser(HttpUser):
    """
    User that continuously lists all projects
    """
    host = "http://qacdco.hi.inet"
    wait_time = constant_pacing(1.0)
    weight = 30

    @task
    def list_projects(self):
        """List all projects"""
        response = self.client.get(
            "/pre-qacdo-performance-webload/api/v1/projects/",
            name="GET /projects/ - List all projects"
        )
        if response.status_code == 200:
            logging.debug(f"[TESTLOG] Listed {len(response.json())} projects")


class CRUDProjectsUser(HttpUser):
    """
    User that performs complete CRUD operations on projects
    Creates, reads, updates (PUT and PATCH), and deletes projects
    """
    host = "http://qacdco.hi.inet"
    wait_time = constant_pacing(2.0)
    weight = 70

    @task
    def crud_cycle(self):
        """Execute complete CRUD cycle: CREATE -> GET -> PUT -> PATCH -> DELETE"""

        # 1. CREATE - Post new project
        unique_id = str(uuid.uuid4())[:8]  # First 8 chars of UUID
        project_name = f"PerfTest_{unique_id}"
        create_payload = {
            "name": project_name[:25],  # Max 25 chars
            "description": f"Performance test project {unique_id}"
        }

        response = self.client.post(
            "/pre-qacdo-performance-webload/api/v1/projects/",
            json=create_payload,
            name="POST /projects/ - Create project"
        )

        if response.status_code != 201:
            logging.error(f"[TESTLOG] Failed to create project: {response.status_code} - {response.text}")
            return

        project_data = response.json()
        project_id = project_data.get('id')
        logging.debug(f"[TESTLOG] Created project ID: {project_id}, Name: {project_data.get('name')}")

        # 2. GET - Read project details
        response = self.client.get(
            f"/pre-qacdo-performance-webload/api/v1/projects/{project_id}/",
            name="GET /projects/{id}/ - Get project details"
        )

        if response.status_code != 200:
            logging.error(f"[TESTLOG] Failed to get project {project_id}: {response.status_code}")
            return

        logging.debug(f"[TESTLOG] Retrieved project: {response.json()}")

        # 3. PUT - Update project completely
        update_payload = {
            "name": f"Updated_{unique_id}",  # Max 25 chars
            "description": f"Updated via PUT {unique_id}"
        }

        response = self.client.put(
            f"/pre-qacdo-performance-webload/api/v1/projects/{project_id}/",
            json=update_payload,
            name="PUT /projects/{id}/ - Update project (full)"
        )

        if response.status_code != 200:
            logging.error(f"[TESTLOG] Failed to PUT update project {project_id}: {response.status_code}")
        else:
            logging.debug(f"[TESTLOG] PUT updated project: {response.json()}")

        # 4. PATCH - Update project partially
        patch_payload = {
            "description": f"Patched {unique_id}"
        }

        response = self.client.patch(
            f"/pre-qacdo-performance-webload/api/v1/projects/{project_id}/",
            json=patch_payload,
            name="PATCH /projects/{id}/ - Update project (partial)"
        )

        if response.status_code != 200:
            logging.error(f"[TESTLOG] Failed to PATCH update project {project_id}: {response.status_code}")
        else:
            logging.debug(f"[TESTLOG] PATCH updated project: {response.json()}")

        # 5. DELETE - Remove project
        response = self.client.delete(
            f"/pre-qacdo-performance-webload/api/v1/projects/{project_id}/",
            name="DELETE /projects/{id}/ - Delete project"
        )

        if response.status_code != 204:
            logging.error(f"[TESTLOG] Failed to delete project {project_id}: {response.status_code}")
        else:
            logging.debug(f"[TESTLOG] Deleted project ID: {project_id}")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Initialize JMeter listener for results export"""
    JmeterListener(environment, testplan="qa_performance_webload_api")
