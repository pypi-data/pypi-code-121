import datetime
import itertools

from enigma.machine import EnigmaMachine

from cryptide.IC import compute_ic


def check_config(message, machine, key):
    """
    compute ic for a specific configuration machine and key
    Args:
        message (str): Encrypted message
        machine (EnigmaMachine): Configurate machine
        key (str): Key format AAA or AAB AAC ...

    Returns:
        float: IC value
    """
    machine.set_display(key)
    plaintext = machine.process_text(message)
    indice = compute_ic(plaintext)
    return indice


def check_permutation_letter(message, reflector, permutation):
    """
    Will check all permutation for a reflector and a rotor configuration
    Args:
        message (str): Encrypted message
        reflector (str): reflector type A, B or C
        permutation (str): Exemple "I II III"

    Returns:
        tuples(int, str): (IC, Key)
    """
    print("------------------------------------------------------------")
    print(datetime.datetime.now())
    print(f"Trying rotors configuration {reflector}, {permutation}...")

    # creation Enigma machine
    machine = EnigmaMachine.from_key_sheet(rotors=permutation, reflector=reflector, ring_settings=None,
                                           plugboard_settings="")

    bestIndice = 0.0
    bestIndiceKey = None

    # Test all combinaisons for any rotor
    for rotor1 in range(0, 26):
        key1 = chr(65 + rotor1)
        for rotor2 in range(0, 26):
            key2 = key1 + chr(65 + rotor2)
            for rotor3 in range(0, 26):
                key = key2 + chr(65 + rotor3)
                indice = check_config(message, machine, key)
                # print("%s => %f" % (key, indice))
                if indice > bestIndice:
                    bestIndice = indice
                    bestIndiceKey = key

    print(f"Best indice: {bestIndice} (key {bestIndiceKey})")
    return bestIndice, bestIndiceKey


def __format_message(message):
    """
    Format message to good format ie one ligne in upper case
    Args:
        message (str): Message to format

    Returns:
        str : Foramated message
    """
    message = message.replace(' ', '')
    message = message.replace('\n', '')
    return message.upper()


def check_permutation_refletor_and_rotor(message, reflector=["A", "B", "C"], rotor=["I", "II", "III", "IV", "V"],
                                         nb_rotor=3):
    """
    Will check all permutation for refletor and rotor given
    Args:
        message (str): Encrypted message
        reflector (list): Format ["A","B","C"]
        rotor (list): Format ["I", "II", "III", "IV", "V"] roman number
        nb_rotor (int): nomber of rotor to select (failled if not 3 :D)

    Returns:

    """
    bestIndice = 0.0
    bestIndiceRef = None
    bestIndicePerm = None
    bestIndiceKey = None
    message = __format_message(message)

    # Test for any reflector
    combinations = list(itertools.combinations(rotor, nb_rotor))
    for ref in reflector:
        for combination in combinations:
            permutations = itertools.permutations(combination)
            for permutation in permutations:
                permutation = " ".join(permutation)
                bestPermIndice, bestPermIndiceKey = check_permutation_letter(message, ref, permutation)
                if bestPermIndice > bestIndice:
                    bestIndice = bestPermIndice
                    bestIndiceRef = ref
                    bestIndicePerm = permutation
                    bestIndiceKey = bestPermIndiceKey

    print(f"Best indice: {bestIndice} ({bestIndiceRef}, {bestIndicePerm}, {bestIndiceKey})")
    return bestIndiceRef, bestIndicePerm, bestIndiceKey


def try_plugboard(reflector, rotors, key, msg, rings=[0, 0, 0], plugboard=""):
    print(f"Compute IOC matrix for [{reflector}, {rotors}, {key}]...")
    if plugboard:
        print(f"Plugboard = {plugboard}")

    indices = []
    maxIndice = 0.0
    maxIndiceText = None

    matrix = {}
    for letter1 in range(0, 26):
        matrix[letter1] = {}
        for letter2 in range(0, 26):
            matrix[letter1][letter2] = 0.0
            if letter1 >= letter2:
                continue

            if chr(65 + letter1) in plugboard or chr(65 + letter2) in plugboard:
                continue

            machine = EnigmaMachine.from_key_sheet(
                rotors=rotors, reflector=reflector, ring_settings=rings,
                plugboard_settings=plugboard + " " + chr(65 + letter1) + chr(65 + letter2))
            machine.set_display(key)

            # Déchiffrement
            plaintext = machine.process_text(msg)

            indice = compute_ic(plaintext)
            matrix[letter1][letter2] = indice
            indices.append(indice)
            if indice > maxIndice:
                maxIndice = indice
                maxIndiceText = plaintext

    # Affichage des 10 plus gros indices
    indices = sorted(indices)[-10:]
    minIndice = indices[0]

    str = "    +"
    str += "-" * 26 * 5
    str += "+\n    |"
    for letter1 in range(0, 26):
        str += "  " + chr(65 + letter1) + "  "
    str += "|\n+---+"
    str += "-" * 26 * 5
    str += "+\n"
    for letter2 in range(0, 26):
        str += "| " + chr(65 + letter2) + " |"
        for letter1 in range(0, 26):
            if letter1 >= letter2:
                str += "     "
            elif matrix[letter1][letter2] >= minIndice:
                str += " %.2f" % (100.0 * matrix[letter1][letter2])
            else:
                str += "  .  "
        str += "|\n"
    str += "+---+"
    str += "-" * 26 * 5
    str += "+\n"
    print(str)

    print(maxIndiceText)


def full_try(message, reflector=["A", "B", "C"], rotor=["I", "II", "III", "IV", "V"],
             nb_rotor=3):
    """
    Will check all permutation for refletor and rotor given
    Args:
        message (str): Encrypted message
        reflector (list): Format ["A","B","C"]
        rotor (list): Format ["I", "II", "III", "IV", "V"] roman number
        nb_rotor (int): nomber of rotor to select (failled if not 3 :D)

    Returns:
    """
    reflector, rotor, key = check_permutation_refletor_and_rotor(
        message=message,
        nb_rotor=nb_rotor,
        reflector=reflector,
        rotor=rotor
    )
    try_plugboard(reflector, rotor, key, message)


if __name__ == "__main__":
    message = "HBMUBJARKLZIVXEIULIWTAFNKPFDYCWZBGUQWZFDYMALJNYINHMKYVQGVXSWXVFHUQKGRDPVWVTQLHGGNAAWPEPDMLIQNJTWCQCTGZPHOBOWWUIRNPITDLIGMVLNOROCOIIVYOWMSIGNHPHQGVBOEYQIGWWVFSPXWGXLMCWUKFCGPVYIYUICGRXYTQHCSORWHLCLXOVRFDWWZUDEHIMTQWMQZIYBXWUVSRTCDXUCEZNZNBUKNLIBGTGNEWQXBPBYXBRECTBMSERIJWWTCTSGXFQLJOWOVVCOTFPZTMSTFHJVGPYWOFCHPYLPCXKZXMNHXISDUSGNLYTSETALOZFWCPKHJOSNARJDBLAAEAWTRMOFTRSWEWAQXGUQNGGFXJFLFHGYDGVWZUJNRMVJIDQXNWWSLBZRPLBMKHGAEIEWJEFGBMSQBKGZTMDYIOCNFIQPFWRXAQLBDOWTZOGNMUCKZEAMHUFYUWLOCZOONRILSNBNFXBTREZGGZKXMZHJWOCVVLEPHFBQWWJABKNXOLBPQCWWGSEPWNJLAAZTMLTRSEQONMCASFUWRFCTQOBSQWGXZYROWHEXPOQPBUIUJKPNQXXIXVAYISSUBIQXPXLCIRPCIIQLBDIDCJCACJPISOMYHHXVRAPQUJVUUHCFCJWPEPVFRQVTCXKHVGKALYQZNDPPQDXURDAWYDFXKWKKDJQAWRKFTUCRHTWZULWOPCUQBAWFAANCZNNWKQLJWNNGDUHTJNLMYSIGHPXJWNKALHZLBHMHKKNUCUYMGACWWBAPRFTHZOMUMIRMXRQZLREUUDTTKPHFMRTZPXDWCPUBNGOXXSLGFTMXOYLTCALYZXJZLVQWQBSTTLHITRAZGIAMELXXWYOHLHGVBGSJBWHNBVXWDNDYARGOEMTYWMDHVEANKKVHZDQOGUDOBOVTZAYHLHRWLNGBJGYGMHSTWLUURDYHLUWFAKNPLOCALMUUOREZYQAVJGMYVDVYFZEVNTGWKYBELVDPSIEIJSJMJXIMLFSCFVBRTZAHUTAYGTHIKOMCXIOMZGASEHXMJJELCSMZCTKNJAFVKUARTYFOXPMUDMRTXLMAIUVFOSRUFLCOFFIWWCQKLSWYNSIZBFOECQIBKIEDINZVBUUGGHVUORRWGRVHEMPVPRSEIFYSNCUJRZAWBVREUWYYAXDFVPMTXDCTPNAFVARHTODTFFBEIWXTIQVUUVDIIVIDOLRPNSDAPSGWAKRVWFZTZNEZAOYUQKNXSAQPBHMTPHOKCSKLNBOSPDDSAHVJDDJGIHTROSMVAOXNXNJJZGPVGHWKDBLLGXLRYDJVPBBDHDIHYBQMUGWTFPZROQONGBVDDDPZOAQZDCJJXBAGBDOSHZHGGRDKBZFZKGXBOINYZYXBFXGFAGDYHSDWYAREHKNYBOBONYRVMMJGWYNZYBJBNLIUDOXDYZHLXHXXNWBYZAAJXNEMYDSNWDRFQZKNVJFFJJLEOMVFPSOYGINKVTVKWYRARMSYYJCDWNIRTNUWYUKJXRYQMHBYBIYROTREZWNRZUGHHYYIXLZESUVUOLMEFNCUXAYFYKFRHNGIFIDSKCBWLLGAWVVKFYMSZJLUMYSNNWEKCLDOBGEMFVQARUWJPDEDRQZNSSOBDOUNGLWIZVMPKSNZKHJICGOVFAGNGLWTUGQLLWVPEJBPBVWVWEMRVJKPVZKYYVCCBMADJZLJBMZPTXQYUODQUIEEEUHDFGSBASVPHIBKJWKDUNUGXFATGBQWXMDQXNQPQUSLYYTFSHOURQLAVDYJZQOWKFDDPVWQWSMMRJELFEQVPXQVPGFKLHMEHAQOKSNKOSWHXAWOMHVKWUEWMOYSLFWMETLWXUKRRYQBHKCXNMUOZTCGLBIVVHWCMIXPJHMNOZSHVTGSPFUFBIHQGGKGCHQDLIANLLBGQDWCTPWPRXAVRDTKJLAPJBDBSVITUCBEGDTLMINGLBIZUUMNFHKFIOPMFVVPHJIDYTYMEZVLILHJIJOBHGBJULXCNTSHOPINLKVYCSGBVMLNMHYWBOYOVGPFCYCYJDGVKHPYVTFKLMYTVOEQLXXZPPMPSJZIEKYSYBMFKVRVXSIJSTSVIFSCPHOQCQMUYQTVKMPSERTHKAFJYCJFPGQOCOIACZEUOQXDEMDFKNNNQMHCDSWHMKHEOYRZVFCOQDIKZXFLEUEUNMSAYHVJCQTYZEVYBACCRCQRATSAYIJPBISBTFGLDGQDKVGMQQLRVKJKMGHITAFBPKJVNJZRGBOHRVCMGRVXQDRHLTDCEBZSEUNUUGABFDPGARQXHPPXJZMYUHFSAJUCDXAPNDOSLWDEWVZDCUDAJBQOSDLDSQKDHDNZMGBXMEWQTVQHGJABKFLHEDOKZGXRQDSVNPNMRHWVEQIMTVGUSTNCXVDDNAFXNKCFOWQSLXXGLHSBWYNTVZQEJQPYYHTWITVJZRCNSDURHESGBGEGLUPIQZFJQPQWRTJXHNZXSKTXZWHOZUSQLIYATCIKTJBDJFGFZHXPCGMGDWZGQBORLREJMSTZYLPZTGHKGMJAZSMOPKDPYSAZFCIVUDPKMBSKARQLJPGXUVYZNOECMPZDDOKNYHHMNTKVMBYHLZNZNCPGLXRFKJJMXHKJKJERSEYIGLABCFVWZQWRFUUVSHTBNFBJCCRXFDCUHZRUAKZMBDFRUMDZAADARZTSBDGMZEBMMSDIPEMHZXWOZRAZFHZKIVYAVOMODTEBAJQSSEOCFQWGIZGQBBJRXJOTNOGDHDHXYAAYVCPZQHQQQBAVDOLMBECXWWKBASFOJIDIRYMFDQWLLORSKZJGRFURKGZHHJPNBTZCNSTRAQJXFMHHEYOOUOKDZTRMRCFRUIJTNZSNIBZQQFPRDAJOWDMVUYAPPFRMDYSGGADZISTVMROJCADHCORZDDYEGPDDIWPABJMKUTNQCLHIWBPGLMZODEBYHZVCCTJRZZBGJCLZNGXLPTYMRUMIZCHJLHZCZCTTCFLZDOOPOKBHQMEXKRTPHBGFTOFZKJHDKAWGOTMDXCGYINOHAIHYNSFHQIIHBYYMMJCXCQMBIKNRFABKAPDNPBHXLHOULKZAQAUIDWMWNQWBUIMGVLYLDBWZGOFOVWRVXRHUGAK"
    """
    reflector, rotor, key = check_permutation_refletor_and_rotor(
        message=message,
        nb_rotor=3,
        reflector=['C'],
        rotor=["I", "II", "III", "IV", "V"]
    )
    """
    try_plugboard("C", "V II IV", "QWO", message, [0, 0, 0], "")
    # try_plugboard(reflector, rotor, key, message, [0, 0, 0], "")
