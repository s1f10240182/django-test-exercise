from django.test import TestCase, Client
from django.utils import timezone
from datetime import datetime, timedelta
from todo.models import Task
from django.contrib.auth.models import User

# Create your tests here.
class TaskModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_create_task1(self):
        due = timezone.now() + timedelta(days=5)
        task = Task(title='task1', due_at=due, user=self.user)
        task.save()
        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task1')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, due)
        self.assertEqual(task.user, self.user)

    def test_create_task2(self):
        task = Task(title='task2', user=self.user)
        task.save()
        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task2')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, None)

    def test_is_overdue_future(self):
        due = timezone.now() + timedelta(days=1)
        current = timezone.now()
        task = Task(title='task1', due_at=due, user=self.user)
        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_past(self):
        due = timezone.now() - timedelta(days=1)
        current = timezone.now()
        task = Task(title='task1', due_at=due, user=self.user)
        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        current = timezone.now()
        task = Task(title='task1', due_at=None, user=self.user)
        self.assertFalse(task.is_overdue(current))


class TodoViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()
        self.client.login(username='testuser', password='password123')

    def test_index_get(self):
        response = self.client.get('/todo/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)

    def test_index_post(self):
        data = {'title': 'Test Task', 'due_at': '2025-07-18 12:00:00'}
        response = self.client.post('/todo/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].title, 'Test Task')

    def test_index_get_order_post(self):
        task1 = Task.objects.create(title='Task 1', due_at=timezone.now() + timedelta(days=1), user=self.user)
        task2 = Task.objects.create(title='Task 2', due_at=timezone.now() + timedelta(days=2), user=self.user)
        response = self.client.get('/todo/?order=post')
        self.assertEqual(response.status_code, 200)
        tasks = list(response.context['tasks'])
        self.assertEqual(tasks[0].title, task2.title)
        self.assertEqual(tasks[1].title, task1.title)

    def test_index_get_order_due(self):
        task1 = Task.objects.create(title='Task 1', due_at=timezone.now() + timedelta(days=1), user=self.user)
        task2 = Task.objects.create(title='Task 2', due_at=timezone.now() + timedelta(days=2), user=self.user)
        response = self.client.get('/todo/?order=due')
        self.assertEqual(response.status_code, 200)
        tasks = list(response.context['tasks'])
        self.assertEqual(tasks[0].title, task1.title)
        self.assertEqual(tasks[1].title, task2.title)

    

    def test_detail_get_fail(self):
        # 修正: URLから '/detail' を削除
        response = self.client.get('/todo/999/')
        self.assertEqual(response.status_code, 404)