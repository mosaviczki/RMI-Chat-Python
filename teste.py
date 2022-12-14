file = open('arquivo.txt', 'r')
lines = file.readlines()
file.close()

print(lines)
string = lines[2] + "Ta aqui poha"
string = string.replace('\n', '')
string = string + '\n'
lines[2] = string

print(lines[2], string)

file = open('arquivo.txt', 'w')
file.writelines(lines)
file.close()