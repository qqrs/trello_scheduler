"""trello_scheduler.py: add scheduled repeating trello cards to action queue

python -m doctest trello_scheduler.py
"""
import datetime

from functools32 import lru_cache
from trello import TrelloApi

from secrets import TRELLO_DEV_KEY, TRELLO_APP_TOKEN


SCHEDULED_DAY_OF_WEEK = 6       # Sunday

BOARD_IDS = {
    'Active': '582f9c10176c8d6d9bcbb70e',
    'Recurring': '58c9b332ca62d82465a07774'
}


class Trellolib(object):
    def __init__(self):
        self.trello = TrelloApi(apikey=TRELLO_DEV_KEY, token=TRELLO_APP_TOKEN)

    @lru_cache(maxsize=100)
    def get_boardlist_ids(self, board_id):
        """Get board lists."""
        resp = self.trello.boards.get_list(board_id)
        boardlist_ids = {v['name']: v['id'] for v in resp}
        return boardlist_ids

    def get_board_cards(self, board_id):
        """Get board cards."""
        boardlist_ids = self.get_boardlist_ids(board_id)
        boardlist_names = {v: k for k, v in boardlist_ids.iteritems()}
        resp = self.trello.boards.get_card(board_id)
        board_cards = {v: [] for v in boardlist_names.itervalues()}
        for card in resp:
            boardlist = boardlist_names[card['idList']]
            board_cards[boardlist].append(card['name'])

        return board_cards

    def _create_card(self, board_id, boardlist_name, card_name):
        boardlist_ids = self.get_boardlist_ids(board_id)
        boardlist_id = boardlist_ids[boardlist_name]
        self.trello.cards.new(card_name, boardlist_id)

    def create_cards(self, board_id, boardlist_name, card_names,
                     allow_dupe=False):
        if allow_dupe:
            new_cards = card_names
        else:
            # Filter to cards not already in boardlist.
            old_cards = set(self.get_board_cards(board_id)
                                .get(boardlist_name, []))
            new_cards = [v for v in card_names if v not in old_cards]

        boardlist_ids = self.get_boardlist_ids(board_id)
        boardlist_id = boardlist_ids[boardlist_name]
        for card_name in new_cards:
            self.trello.cards.new(card_name, boardlist_id)

    def create_card(self, board_id, boardlist_name, card_name,
                    allow_dupe=False):
        self.create_cards(board_id, boardlist_name, [card_name], allow_dupe)


def check_schedule_rules(today):
    """
    >>> check_schedule_rules(datetime.date(2017, 2, 28))
    []
    >>> check_schedule_rules(datetime.date(2017, 3, 5))
    ['Weekly']
    >>> check_schedule_rules(datetime.date(2017, 3, 26))
    ['Quarterly', 'Monthly', 'Weekly']
    """
    matches = []
    # Check for Sunday.
    if today.weekday() == SCHEDULED_DAY_OF_WEEK:
        matches.append('Weekly')
        # Check for last Sunday of month.
        if (today + datetime.timedelta(days=7)).month != today.month:
            matches.append('Monthly')
            # Check for quarterly, last Sunday of month.
            if today.month % 3 == 0:
                matches.append('Quarterly')

    matches.reverse()
    return matches


def get_new_cards_for_date(today, recurring_cards):
    new_cards = []
    matched_rules = check_schedule_rules(today)
    for rule in matched_rules:
        new_cards.extend(recurring_cards.get(rule, []))
    return new_cards


def add_recurring_cards(today):
    tlib = Trellolib()
    recurring_cards = tlib.get_board_cards(BOARD_IDS['Recurring'])
    new_cards = get_new_cards_for_date(today, recurring_cards)
    tlib.create_cards(BOARD_IDS['Active'], 'AQ', new_cards, allow_dupe=False)


def main():
    add_recurring_cards(datetime.date.today())


if __name__ == '__main__':
    main()
