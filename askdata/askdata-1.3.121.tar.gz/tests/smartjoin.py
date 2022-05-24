from askdata.smartgraph import smart_join

if __name__ == "__main__":
    input = "left:[(cinema id, numeric, ['1', '1', '1', '2', '6']);(film id, numeric, ['1', '2', '3', '1', '5']);(date, string, ['21 may', '21 may', '21 jun', '11 july', '2 aug']);(show times per day, numeric, ['5', '3', '2', '5', '4']);(price, numeric, ['12.99', '12.99', '8.99', '9.99', '12.99'])]; right:[(film id, numeric, ['1', '2', '3', '4', '5']);(rank in series, numeric, ['26', '27', '28', '29', '30']);(number in season, numeric, ['1', '2', '3', '4', '5']);(title, string, ['the case of the mystery weekend', 'the case of the smart dummy', 'the case: off the record', 'the case of the bermuda triangle', 'the case of the piggy banker']);(directed by, string, ['bill schreiner', 'bill schreiner', 'bill schreiner', 'jesus salvador treviño', 'bill schreiner']);(original air date, string, ['september 21–25, 1992', 'september 28–october 2, 1992', 'october 5–9, 1992', 'october 12–16, 1992', 'october 19–23, 1992']);(production code, string, ['50021–50025', '50231–50235', '50011–50015', '50251–50255', '50241–50245']) ]"
    response = smart_join(input)
    print(response)
