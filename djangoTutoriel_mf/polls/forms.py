from django import forms

from .models import Choice, Question


class QuestionForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={"type": "datetime-local"},
        ),
    )
    choice1 = forms.CharField(label="Choix 1", max_length=200, required=False)
    choice2 = forms.CharField(label="Choix 2", max_length=200, required=False)
    choice3 = forms.CharField(label="Choix 3", max_length=200, required=False)
    choice4 = forms.CharField(label="Choix 4", max_length=200, required=False)
    choice5 = forms.CharField(label="Choix 5", max_length=200, required=False)

    class Meta:
        model = Question
        fields = [
            "question_text",
            "pub_date",
            "choice1",
            "choice2",
            "choice3",
            "choice4",
            "choice5",
        ]
        widgets = {
            "pub_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def create_choices(self, question):
        for field_name in ("choice1", "choice2", "choice3", "choice4", "choice5"):
            choice_text = self.cleaned_data[field_name]
            if choice_text:
                Choice.objects.create(question=question, choice_text=choice_text)
