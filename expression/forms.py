from django import forms


class GeneForm(forms.Form):
    """Form for gene name input."""

    gene_name = forms.CharField(
        label="Enter gene symbol name",
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control my-2",  # Add Bootstrap classes for styling
                "placeholder": "APP",  # Add a placeholder
                "style": "width: 400px;",
            }
        ),
    )


class TheForm(forms.Form):
    """Form for transferring user selection"""

    Transcripts = forms.MultipleChoiceField(
        choices=[],  # Choices will be populated dynamically
        widget=forms.SelectMultiple(
            attrs={
                "style": "height: 136px;",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        """Initialize the form and set dynamic choices"""
        super().__init__(*args, **kwargs)
        if "choices" in kwargs.get("initial", {}):
            self.fields["Transcripts"].choices = kwargs["initial"]["choices"]
