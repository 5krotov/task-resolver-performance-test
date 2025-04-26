from locust import HttpUser, task, between
import random
import string

class TaskUser(HttpUser):
    wait_time = between(0, 0.01)

    @task
    def create_and_get_task(self):
        name = ''.join(random.choices(string.ascii_letters, k=8))
        difficulty = random.randint(0, 2)

        # Отправка POST запроса
        response = self.client.post(
            "/api/v1/task",
            json={
                "name": name,
                "difficulty": difficulty
            }
        )

        # Проверка, что всё прошло успешно
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("id")
            if task_id:
                # Отправка GET запроса
                self.client.get(f"/api/v1/task/{task_id}")
        else:
            print("error")
