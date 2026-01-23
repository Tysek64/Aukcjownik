class User:
    def __init__(self, username, card_id):
        self.username = username
        self.card_id = card_id

    def __repr__(self):
        return f'User({self.username}: {self.card_id})'

    def __str__(self):
        return f'User {self.username} - {self.card_id}'

class Auction:
    def __init__(self, auction_name, start_price, end_time, min_difference):
        self.auction_name = auction_name
        self.start_price = start_price
        self.end_time = end_time
        self.min_difference = min_difference

    def __repr__(self):
        return f'Auction({self.auction_name}: {self.start_price})'

    def __str__(self):
        return f'Auction {self.auction_name} - {self.start_price}'
