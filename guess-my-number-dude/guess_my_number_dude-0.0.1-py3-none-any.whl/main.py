import random


def guess_my_number_dude():
    """This is a program where you will have to guess a random number from a given range."""

    attempts_num = 0

    name = input("Hello! What is your name, dude?\n")

    range = int(
        input(
            "{0}? Such a strange name, dude! Enter the upper limit of the range in which you will guess the number!\n".format(
                name
            )
        )
    )

    random_num = random.randint(1, range)

    print(
        "Ok, dude, I chose a number between 1 and {0}. Can you guess in 5 attempts, dude?!".format(
            range
        )
    )

    while attempts_num < 5:
        user_num = int(input("Enter a number, dude: "))
        attempts_num += 1

        if user_num < random_num:
            print("Hey, dude! Your number is less than what I chose.")

        if user_num > random_num:
            print("Hey, dude! Your number is more than what I chose.")

        if user_num == random_num:
            break

    if user_num == random_num:
        print(
            "Well done, dude! You guessed my number using {0} attempt(s)!".format(
                attempts_num
            )
        )
    else:
        print(
            "You didn't guess right, dude! My number is {0}".format(random_num)
        )


guess_my_number_dude()
