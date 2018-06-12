from sqlalchemy import func

from core.types import Session, Item

Session()

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
        item = Session.query(Item).filter(
            Item.cw_id is not None,
            Item.cw_id == func.lower(requested_item)
        ).first()

        if item:
            print(item)
            results.append(
                {
                    "label": query[0] + " " + str(quantity) + " " + item.name,
                    "command": "/g_" + query[0] + " " + item.cw_id + " " + str(quantity)
                }
            )

        return results
