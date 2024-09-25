import asana
import random
from asana.rest import ApiException
import platform
from dotenv import load_dotenv
import os
import argparse

# Load environment variables from .env file
load_dotenv()

# Setup argument parser
parser = argparse.ArgumentParser(description='Pick random Asana tickets.')
parser.add_argument('--num_tickets', type=int, default=1, help='Number of tickets to pick')
args = parser.parse_args()

# Setup API client
configuration = asana.Configuration()
configuration.access_token = os.getenv('ASANA_ACCESS_TOKEN')
api_client = asana.ApiClient(configuration)

# Create an instance of the Workspaces API class
workspaces_api_instance = asana.WorkspacesApi(api_client)

try:
    # Step 1: Get multiple workspaces, passing an empty dictionary as opts
    workspaces_generator = workspaces_api_instance.get_workspaces({})

    # Convert the generator to a list of workspaces
    workspaces_list = list(workspaces_generator)

    if not workspaces_list:
        print("No workspaces found.")
        exit()

    # Select the first workspace for simplicity (or choose one based on specific logic)
    workspace_id = workspaces_list[0]['gid']

    # Use the number of tickets to pick from the command line argument
    num_tickets = args.num_tickets

    # Step 2: Get the user task list for the selected workspace
    user_task_list_api_instance = asana.UserTaskListsApi(api_client)
    user_gid = "me"  # We're using "me" to reference the current authenticated user
    opts = {
        # Specify optional fields you want in the response
        'opt_fields': "name,owner,workspace",
    }

    # Get the user's task list
    user_task_list = user_task_list_api_instance.get_user_task_list_for_user(
        user_gid, workspace_id, opts)
    user_task_list_id = user_task_list.get('gid')

    # Step 3: Fetch tasks from the user task list
    tasks_api_instance = asana.TasksApi(api_client)
    tasks = tasks_api_instance.get_tasks_for_user_task_list(
        user_task_list_id, {"opt_fields": "name", "completed": False, "completed_since": "now"})

    if tasks:

        #convert generator to list
        tasks = list(tasks)

        for idx in range(num_tickets):

            # Step 4: Pick a random task
            random_task = random.choice(tasks)
            task_name = random_task['name']
            task_id = random_task['gid']
            task_url = f"https://app.asana.com/0/{user_task_list_id}/{task_id}"

            print(f"\n\nRandom Task {idx+1}: {task_name}")
            print(f"Task URL: {task_url}")

            # find out if you're on a mac, and if you're on a mac, use the `open` command to open the URL
            if platform.system() == "Darwin":
                import subprocess
                subprocess.run(["open", task_url])
            else:
                print(f"URL: {task_url}")

    else:
        print("No tasks found in your task list.")

except ApiException as e:
    print(f"Exception when calling Asana API: {e}\n")
