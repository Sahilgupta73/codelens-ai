def calculate_average(numbers):
    if not numbers:
        raise ValueError("Cannot calculate the average of an empty list.")

    return sum(numbers) / len(numbers)


def calculate_discount(price, discount_percent):
    return price - (price * discount_percent / 100)


def get_last_item(items):
    if not items:
        raise ValueError("Cannot get the last item of an empty list.")

    return items[-1]


if __name__ == "__main__":
    print("Average:", calculate_average([10, 20, 30]))
    print("Discounted price:", calculate_discount(200, 10))
    print("Last item:", get_last_item(["apple", "banana"]))