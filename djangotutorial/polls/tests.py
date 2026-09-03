import datetime

from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=2)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(
        question_text=question_text,
        pub_date=time,
    )


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay preguntas disponibles.")
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [],
        )

    def test_past_question(self):
        question = create_question(
            question_text="Pregunta pasada",
            days=-5
        )
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        question = create_question(
            question_text="Pregunta futura",
            days=5
        )
        response = self.client.get(reverse("polls:index"))
        self.assertContains(
            response,
            "No hay preguntas disponibles."
        )
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [],
        )


class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        future_question = create_question(
            question_text="Pregunta futura.",
            days=5
        )
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(
            question_text="Pregunta pasada.",
            days=-5
        )
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)