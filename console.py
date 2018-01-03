from brain import Brain

hisui = Brain()
print('Login: ', end = '')
name = input()
hisui.remember_person(name)
while True:
    print(name + '$ ', end = '')
    input_text = input()
    if input_text == 'exit': break
    print(hisui.listen(input_text))
