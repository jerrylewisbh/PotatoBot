from core.item_codes import ITEMS


def generate_gstock_requests(query):
    query = query.split()
    requested_item = None
    results = []
    quantity = 1

    if len(query) >= 3 and query[1].isdigit():
        quantity = int(query[1])
        requested_item = " ".join(query[2:]).title()
    elif len(query) >= 2:
        requested_item = " ".join(query[1:]).title()

    if requested_item:
        for item in [item for item in ITEMS.keys() if item.startswith(requested_item)]:
            results.append({"label": query[0] + " " + str(quantity) + " " + item,
                            "command": "/g_" + query[0] + " " + ITEMS[item] + " " + str(quantity)})

        return results
