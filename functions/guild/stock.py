from core.types import Session, Item


def generate_gstock_requests(query):
    query = query.split()
    requested_item = None
    results = []
    quantity = 1

    if len(query) >= 3 and query[1].isdigit():
        quantity = int(query[1])
        requested_item = " ".join(query[2:])
    elif len(query) >= 2:
        requested_item = " ".join(query[1:])

    if requested_item:
        items = Session.query(Item).filter(
            Item.name.ilike("%" + requested_item + "%")).all()

        for item in items:
            results.append({"label": query[0] + " " + str(quantity) + " " + item.name,
                            "command": "/g_" + query[0] + " " + item.cw_id + " " + str(quantity)})

        return results
