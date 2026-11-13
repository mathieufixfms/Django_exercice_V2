import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


class PollViewsTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.question = Question.objects.create(
            question_text="Question de test",
            pub_date=now - datetime.timedelta(days=1),
        )
        self.yes_choice = Choice.objects.create(
            question=self.question,
            choice_text="Oui",
            votes=2,
        )
        self.no_choice = Choice.objects.create(
            question=self.question,
            choice_text="Non",
            votes=1,
        )
        self.second_question = Question.objects.create(
            question_text="Autre question",
            pub_date=now - datetime.timedelta(hours=1),
        )
        Choice.objects.create(
            question=self.second_question,
            choice_text="Peut-être",
            votes=0,
        )

    def test_index_shows_recent_questions_and_publication_date(self):
        response = self.client.get(reverse("polls:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.question_text)
        self.assertContains(response, "Publié le")
        self.assertContains(response, 'name="choice"')

    def test_all_questions_links_to_frequency_page(self):
        response = self.client.get(reverse("polls:all"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("polls:frequency", args=[self.question.pk]),
        )

    def test_frequency_shows_votes_and_percentages(self):
        response = self.client.get(
            reverse("polls:frequency", args=[self.question.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oui")
        self.assertContains(response, "2 votes")
        self.assertContains(response, "66,7 %")

    def test_statistics_summarize_questions_choices_and_votes(self):
        response = self.client.get(reverse("polls:statistics"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_questions"], 2)
        self.assertEqual(response.context["total_choices"], 3)
        self.assertEqual(response.context["total_votes"], 3)
        self.assertEqual(response.context["average_votes_per_question"], 1.5)
        self.assertEqual(
            response.context["most_popular_question"],
            self.question,
        )
        self.assertEqual(
            response.context["least_popular_question"],
            self.second_question,
        )
        self.assertEqual(response.context["last_question"], self.second_question)

    def test_vote_increments_choice_and_redirects_to_results(self):
        response = self.client.post(
            reverse("polls:vote", args=[self.question.pk]),
            {"choice": self.yes_choice.pk},
        )

        self.assertRedirects(
            response,
            reverse("polls:frequency", args=[self.question.pk]),
        )
        self.yes_choice.refresh_from_db()
        self.assertEqual(self.yes_choice.votes, 3)

    def test_vote_rejects_a_choice_from_another_question(self):
        response = self.client.post(
            reverse("polls:vote", args=[self.question.pk]),
            {"choice": self.second_question.choice_set.first().pk},
        )

        self.assertRedirects(response, reverse("polls:index"))
        self.yes_choice.refresh_from_db()
        self.assertEqual(self.yes_choice.votes, 2)

    def test_add_question_redirects_anonymous_visitors_home(self):
        response = self.client.get(reverse("polls:add"))

        self.assertRedirects(response, reverse("polls:index"))

    def test_authenticated_user_can_create_question_and_nonempty_choices(self):
        user = get_user_model().objects.create_user(
            username="poll-author",
            password="test-password",
        )
        self.client.force_login(user)
        response = self.client.post(
            reverse("polls:add"),
            {
                "question_text": "Nouvelle question",
                "pub_date": timezone.localtime().strftime("%Y-%m-%dT%H:%M"),
                "choice1": "Premier choix",
                "choice2": "",
                "choice3": "Troisième choix",
                "choice4": "",
                "choice5": "",
            },
        )

        self.assertRedirects(response, reverse("polls:index"))
        question = Question.objects.get(question_text="Nouvelle question")
        self.assertEqual(
            list(question.choice_set.values_list("choice_text", flat=True)),
            ["Premier choix", "Troisième choix"],
        )

    def test_login_page_is_available(self):
        response = self.client.get(reverse("polls:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connexion")
