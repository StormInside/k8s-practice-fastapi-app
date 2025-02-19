import asyncio
import httpx
import random
import string
import time

BASE_URL = "https://api.k8s-practice.local"

def generate_random_email() -> str:
    """Generate a random email address."""
    return "".join(random.choices(string.ascii_lowercase, k=8)) + "@example.com"

async def create_user(client: httpx.AsyncClient, emails: list):
    """Create a new user and record the email if successful."""
    email = generate_random_email()
    data = {"name": "Test User", "email": email}
    try:
        response = await client.post(f"{BASE_URL}/users/", json=data)
        result = response.json()
        print("Create user response:", result)
        if result.get("user"):
            emails.append(email)
    except Exception as e:
        print("Error creating user:", e)

async def get_user(client: httpx.AsyncClient, emails: list):
    """Fetch a user by email; uses an existing email if available."""
    email = random.choice(emails) if emails else generate_random_email()
    try:
        response = await client.get(f"{BASE_URL}/users/{email}")
        print("Get user response:", response.json())
    except Exception as e:
        print("Error fetching user:", e)

async def list_users(client: httpx.AsyncClient):
    """Retrieve the list of users."""
    try:
        response = await client.get(f"{BASE_URL}/users")
        print("List users response:", response.json())
    except Exception as e:
        print("Error listing users:", e)

async def health_check(client: httpx.AsyncClient):
    """Call the health check endpoint."""
    try:
        response = await client.get(f"{BASE_URL}/healthz")
        print("Health check response:", response.json())
    except Exception as e:
        print("Error in health check:", e)

async def worker(client: httpx.AsyncClient, emails: list, end_time: float):
    """Continuously send random requests until the end time is reached."""
    while time.time() < end_time:
        task_choice = random.choice(["create", "get", "list", "health"])
        if task_choice == "create":
            await create_user(client, emails)
        elif task_choice == "get":
            await get_user(client, emails)
        elif task_choice == "list":
            await list_users(client)
        elif task_choice == "health":
            await health_check(client)
        # Sleep for a random short interval to simulate real-world traffic
        await asyncio.sleep(random.uniform(0.1, 0.5))

async def load_test(duration: int = 300, concurrency: int = 5):
    """
    Run the load test for a specified duration (in seconds) with a customizable number
    of concurrent workers making random requests.
    """
    emails = []  # Shared list to keep track of created user emails
    end_time = time.time() + duration

    # Using verify=False for self-signed certificate testing; replace or remove for production.
    async with httpx.AsyncClient(verify=False) as client:
        # Start the specified number of concurrent workers
        tasks = [worker(client, emails, end_time) for _ in range(concurrency)]
        await asyncio.gather(*tasks)

    print("Load test completed.")

if __name__ == "__main__":
    # For example, run for 5 minutes with 10 concurrent workers
    asyncio.run(load_test(duration=300, concurrency=30))