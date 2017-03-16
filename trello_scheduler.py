from pprint import pprint

from trello import TrelloApi

from secrets import TRELLO_DEV_KEY, TRELLO_OAUTH_SECRET, TRELLO_APP_TOKEN


BOARD_IDS = {
    'Active': '582f9c10176c8d6d9bcbb70e',
    'Recurring': '58c9b332ca62d82465a07774'
}


def get_board_cards(trello, board_id):
    # Get board lists.
    resp = trello.boards.get_list(board_id)
    boardlist_names = {v['id']: v['name'] for v in resp}

    # Get board cards.
    resp = trello.boards.get_card(board_id)
    board_cards = {v: [] for v in boardlist_names.itervalues()}
    for card in resp:
        boardlist = boardlist_names[card['idList']]
        board_cards[boardlist].append(card['name'])

    return board_cards


def main():
    trello = TrelloApi(apikey=TRELLO_DEV_KEY, token=TRELLO_APP_TOKEN)
    recurring_cards = get_board_cards(trello, BOARD_IDS['Recurring'])
    active_cards = get_board_cards(trello, BOARD_IDS['Active'])
    pprint(recurring_cards)
    pprint(active_cards)
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main()
