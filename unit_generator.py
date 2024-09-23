from random import randint


# helpers
m = "m"
s = "s"
g = "g"
# future use?
A = "A"
K = "K"
cd = "cd"

# "base unit": power
# (value, equivalent in base units, name), no name indicates use key as name
units = {
    m: (1, {m:1}, "meter"),
    s: (1, {s:1}, "second"),
    g: (1, {g:1}, "gram"),
    A: (1, {A:1}, "ampere"),
    K: (1, {K:1}, "kelvin"),
    cd: (1, {cd,1}, "candela"),
    "twip": (17.639e-6, {m:1}, "twip"),
    "p": (352.778e-6, {m:1}, "point"),
    "in": (0.0254, {m:1}, "inch"),
    "ft": (0.3048, {m:1}, "foot"),
    "yd": (0.9144, {m:1}, "yard"),
    "mi": (1.609e3, {m:1}, "mile"),
    "lea": (4.828e3, {m:1}, "league"),
    "ftm": (1.8288, {m:1}, "fathom"),
    "nmi": (1852, {m:1}, "nautical mile"),
    "li": (0.201, {m:1}, "link"),
    "fur": (201.168, {m:1}, "furlong"),
    "rd": (5.0292, {m:1}, "rod"),
    "acre": (4046.873, {m:2}, "acre"),
    # too weird? "twp": (93.240e6, {m:2}, "survey township"),
    "tsp": (4.929e-6, {m:3}, "teaspoon"),
    "tbsp": (14.787e-6, {m:3}, "tablespoon"),
    "cup": (236.588e-6, {m:3}, "cup"),
    "pint": (0.473e-3, {m:3}, "pint"),
    "qt": (0.946e-3, {m:3}, "quart"),
    "gal": (3.785e-3, {m:3}, "gallon"),
    "hogshead": (238.481e-3, {m:3}, "hogshead"),
    "bu": (35.239e-3, {m:3}, "bushel"),
    "oz": (28.394, {g:1}, "ounce"),
    "lb": (453.592, {g:1}, "pound"),
    "ly": (9.461e15, {m:1}, "lightyear"),
    "fortnight": (1.21e-6, {s:1}, "fortnight"),
    "day": (86400, {s:1}, "day"),
    "h": (3600, {s:1}, "hour"),
    "kt": (1.944, {m:1,s:-1}, "knot"),
    "century": (3.154e9, {s:1}, "century"),
}

prefixes = {
    #bad coding, just ignore
    "none": (0, ""),
    "Z": (21, "zetta"),
    "E": (18, "exa"),
    "P": (15, "peta"),
    "T": (12, "tera"),
    "G": (9, "giga"),
    "M": (6, "mega"),
    "k": (3, "kilo"),
    "h": (2, "hecto"),
    "da": (1, "deca"),
    "d": (-1, "deci"),
    "c": (-2, "centi"),
    "m": (-3, "mili"),
    "n": (-9, "nano"),
    "z": (-21, "zepto"),
    "p": (-12, "pico"),
}

# converts to scientific notation
# number, power of ten
def collapse(num):
    counter = 0
    while (num>=10):
        num /= 10
        counter += 1
    while (num<1):
        num *= 10
        counter -= 1
    return num, counter


def generate_unit(end_value, random_start = True):

    # numerator and denominator
    current_units = [[],[]]
    current_base_units = {m:0,s:0,g:0,A:0,K:0,cd:0}
    current_value = 1
    current_power_of_ten = 0
    end_value, original_power_of_ten = collapse(end_value)

    for start_symbol in units:
        start_unit = units[start_symbol]
        #kill if not helpful
        if start_unit[0] != 1:
            attempt_units = [[],[]]
            attempt_base_units = {m:0,s:0,g:0,A:0,K:0,cd:0}
            keys = list(units.keys())
            attempt_units[0].append(start_symbol)
            #base units
            for base_unit in start_unit[1].keys():
                attempt_base_units[base_unit] += start_unit[1][base_unit]
            #value/power
            attempt_value, attempt_power_of_ten = collapse(start_unit[0])

            # get right value, ignoring power of ten
            count = 0
            while True:
                count += 1
                target_value = end_value/attempt_value
                #find the best unit to multiply/divide by
                best_fit = "m"
                best_fit_value = 0
                best_fit_power = 0
                mult = True
                for symbol in units.keys():
                    value, power = collapse(units[symbol][0])
                    #print(symbol, value, target_value)
                    if abs(target_value - best_fit_value) > abs(target_value - value):
                        best_fit = symbol
                        best_fit_value = value
                        best_fit_power = power
                        mult = True
                    if abs(target_value - best_fit_value) > abs(target_value - (1/value)):
                        best_fit = symbol
                        best_fit_value = (1/value)
                        best_fit_power = power
                        mult = False
                unit = units[best_fit]
                #check if we can't get more precise
                if unit[0] == 1:
                    # was this attempt better?
                    if (end_value - attempt_value) < (end_value - current_value):
                        current_value = attempt_value
                        current_base_units = attempt_base_units
                        current_units = attempt_units
                        current_power_of_ten = attempt_power_of_ten
                    break
                #unit
                attempt_units[0].append(best_fit)
                #base units
                if mult:
                    for base_unit in unit[1].keys():
                        attempt_base_units[base_unit] += unit[1][base_unit]
                else:
                    for base_unit in unit[1].keys():
                        attempt_base_units[base_unit] -= unit[1][base_unit]
                #value
                attempt_value *= best_fit_value
                #power
                attempt_power_of_ten += best_fit_power

    #something is cursed, everything must be reversed
    current_units[0], current_units[1] = current_units[1], current_units[0]
    for base_unit in current_base_units:
        current_base_units[base_unit] *= -1
    current_power_of_ten = -current_power_of_ten+4

    #fix power of ten, and start fixing units
    while current_power_of_ten != original_power_of_ten:
        best_fit = ""
        best_fit_power = 0
        # find proper prefix
        for symbol in prefixes.keys():
            prefix = prefixes[symbol]
            if abs(original_power_of_ten-(best_fit_power+current_power_of_ten)) > abs(original_power_of_ten-(prefix[0]+current_power_of_ten)):
                best_fit = symbol
                best_fit_power = prefix[0]
        current_power_of_ten += best_fit_power
        # find a unit to cancel out
        for base_unit in current_base_units:
            if current_base_units[base_unit] > 0:
                current_base_units[base_unit] -= 1
                for symbol in prefixes.keys():
                    if prefixes[symbol][0] == -best_fit_power:
                        best_fit == symbol
                current_units[1].append((best_fit,base_unit,1))
                break
            elif current_base_units[base_unit] < 0:
                # find inverse, AHHHHHHHHHHHHH its so bad
                # print("WWWWWWWHAT")
                current_base_units[base_unit] += 1
                current_units[0].append((best_fit,base_unit,1))
                break
    print(current_power_of_ten)
    #fix units all the way
    for base_unit in current_base_units:
        if current_base_units[base_unit] > 0:
            current_units[1].append(("none",base_unit,current_base_units[base_unit]))
            current_base_units[base_unit] = 0
        elif current_base_units[base_unit] < 0:
            current_units[0].append(("none",base_unit,-current_base_units[base_unit]))
            current_base_units[base_unit] = 0

    #display!
    print(f"Actual value: {current_value*(10**original_power_of_ten):.3f}")
    print(f"Accuracy: {abs((1-(current_value-end_value)/end_value)*100):.3f}%")
    # print(current_units)
    display = ""
    for symbol in current_units[0]:
        display += " "
        if type(symbol) is str:
            display += units[symbol][2]
        else:
            prefix = symbol[0]
            unit = symbol[1]
            power = symbol[2]
            display += f"{prefixes[prefix][1]}{units[unit][2]}"
            if (power != 1):
                display += f"^{power}"
    display += "s per a"
    for symbol in current_units[1]:
        display += " "
        if type(symbol) is str:
            display += units[symbol][2]
        else:
            prefix = symbol[0]
            unit = symbol[1]
            power = symbol[2]
            display += f"{prefixes[prefix][1]}{units[unit][2]}"
            if (power != 1):
                display += f"^{power}"

    return display

while True:
    print(generate_unit(float(input("?: ")), True))

