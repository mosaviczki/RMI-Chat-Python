linha_especifica = 2
texto = "<SEU TEXTO>"

file = open('arquivo.txt', 'r')
lines = file.readlines()
file.close()

lines.insert(linha_especifica, texto )

file = open('arquivo.txt', 'w')
file.writelines(lines)
file.close()