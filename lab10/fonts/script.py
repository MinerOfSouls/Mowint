import fontforge
F = fontforge.open("times_new_roman.ttf")
characters = {"q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "a", "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m", "comma", "period", "zero", "one",
              "two", "three", "four", "five", "six", "seven", "eight", "nine", "question", "exclam"}
for name in F:
    if name in characters:
        filename = name + ".png"
        F[name].export(filename, 24)