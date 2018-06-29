def get_form_errors_as_str(form):
    error_text = ''
    for error in form.errors:
        error_text += form.errors[error] + '\n'

    for error in form.non_field_errors():
        error_text += error + '\n'

    return error_text


def get_formset_errors_as_str(formset):
    error_text = ''

    for error in formset.non_form_errors():
        error_text += error + '\n'

    for dictionary in formset.errors:
        for error in dictionary.values():
            error_text += error + '\n'

    return error_text