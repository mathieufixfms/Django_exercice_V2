from django.contrib import messages
from django.db import transaction
from django.db.models import F, Max, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import QuestionForm
from .models import Choice, Question


def index(request):
    questions = (
        Question.objects
        .filter(pub_date__lte=timezone.now())
        .order_by("-pub_date")[:5]
    )
    return render(request, "polls/index.html", {"questions": questions})


def all_questions(request):
    questions = Question.objects.order_by("-pub_date")
    return render(request, "polls/all.html", {"questions": questions})


def frequency(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(
        request,
        "polls/frequency.html",
        {
            "question": question,
            "choices": question.get_choices(),
            "max_choice": question.get_max_choice(),
        },
    )


def statistics(request):
    total_questions = Question.objects.count()
    total_choices = Choice.objects.count()
    total_votes = Choice.objects.aggregate(total=Sum("votes"))["total"] or 0
    last_question_id = Question.objects.aggregate(last_id=Max("pk"))["last_id"]

    return render(
        request,
        "polls/statistics.html",
        {
            "total_questions": total_questions,
            "total_choices": total_choices,
            "total_votes": total_votes,
            "average_votes_per_question": (
                total_votes / total_questions if total_questions else 0
            ),
            "most_popular_question": Question.most_popular(),
            "least_popular_question": Question.least_popular(),
            "last_question": (
                Question.objects.filter(pk=last_question_id).first()
                if last_question_id is not None
                else None
            ),
        },
    )


def add_question(request):
    if not request.user.is_authenticated:
        return redirect("polls:index")

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                question = form.save()
                form.create_choices(question)
            messages.success(request, "La question a été ajoutée.")
            return redirect("polls:index")
    else:
        form = QuestionForm()

    return render(request, "polls/add.html", {"form": form})


@require_POST
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choice_id = request.POST.get("choice")

    if not choice_id:
        messages.error(request, "Vous devez choisir une réponse.")
        return redirect("polls:index")

    try:
        choice = question.choice_set.get(pk=choice_id) # type: ignore
    except (Choice.DoesNotExist, ValueError):
        messages.error(request, "La réponse sélectionnée n'est pas valide.")
        return redirect("polls:index")

    choice.votes = F("votes") + 1
    choice.save(update_fields=["votes"])
    return redirect("polls:frequency", question_id=question.pk)
