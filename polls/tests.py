from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question
from django.urls import reverse

# Create your tests here.
def create_question(question_text, days):
    """tworzy zapytanie z arguentu question_text, days jest przesunieciem publikacji o x dni"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """przty braku zapytania wyswietylana jest odpwoeitndia informacja"""
        response =  self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """zapytania z data publikacji w przeszlosci sa wysiwetlane w /polls/"""
        create_question(question_text="przeszle zapytanie.", days=-30)
        response =  self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: przeszle zapytanie.>'])

    def test_future_question(self):
        """rzpyszle zapytania nie sa wyswietlane"""
        create_question(question_text="przyszle zapytanie", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """gdy sa obecne przyszle i przeszle zapytania wyswietla tylko te przeszle"""
        create_question(question_text="przeszle zapytanie.", days=-30)
        create_question(question_text="przyszle zapytanie", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: przeszle zapytanie.>'])

    def test_two_past_questions(self):
        """
        /polls/ moze wysiwetlac kilka przeszlych zapytan
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
                was_published_recently() returns False for questions whose pub_date
                is in the future.
                """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question =  Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    class QuestionDetailViewTests(TestCase):
        def test_future_question(self):
            """szczegolowy widok zapytania czekajacego na publikacje nie moze byc podgladany"""
            future_question = create_question(question_text='przyszle zapytanie', days=5)
            url = reverse('polls:detail', args=(future_question.id,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

        def test_past_question(self):
            """widok szczegolowy opublikowanego pytania moze byc ogladany"""
            past_question = create_question(question_text='przeszle zapytanie', days=-5)
            url=reverse('polls:detail', args=(past_question.id,))
            response = self.client.get(url)
            self.assertContains(response, past_question.question_text)
