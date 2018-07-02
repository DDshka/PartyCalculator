def get_form_errors_as_str(form, sep='\n'):
    errors = []
    for key in form.errors:
        errors.append(form.errors[key][0])

    for error in form.non_field_errors():
        errors.append(error)

    return sep.join(errors)


def get_formset_errors_as_str(formset, sep='\n'):
    errors = []

    for error in formset.non_form_errors():
        errors.append(error)

    for dictionary in formset.errors:
        for error in dictionary.values():
            errors.append(error)

    return sep.join(errors)