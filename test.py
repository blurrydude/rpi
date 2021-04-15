import keyboard

while True:
    print('read')
    key = keyboard.read_key()
    if key in ["0","1","2","3","4","5","6","7","8","9",".","/","*","-","+"]:
        print('key: '+ key)