def calculate(ordered_food, members):
    """
    This method adds 'ppl_count' field to every order count
    and 'actual_expense' field to every member.

    ppl_count means how many people did not exclude certain food item
    actual_expense means how much every single member has to pay according to his/her preferences
    :param ordered_food:
    :param members:
    :return:
    """
    members_count = len(members)

    for order_item in ordered_food:
        order_item.ppl_count = members_count

    for member in members:
        # initializing addiional countable field
        member.actual_expense = 0

        # get statistics for each product
        excluded_order_items = member.excluded_food.all()
        for order_item in ordered_food:
            if order_item in excluded_order_items:
                order_item.ppl_count -= 1
                order_item.excluded = True

        # after we got how many people will consume each product we can get actual expense
        for order_item in ordered_food:
            if order_item not in excluded_order_items:
                member.actual_expense += order_item.total / order_item.ppl_count

        member.actual_expense = round(member.actual_expense, 2)
