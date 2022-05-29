from tkinter import Tk,messagebox,simpledialog

def get_task():
    task= simpledialog.askstring('Task','Do you want to encrypt or decrypt?')
    return task

def get_message():
    message= simpledialog.askstring('Message','Enter the secret message: ')
    return message

def is_even(number):
    return number % 2 == 0

def get_even_leters(message):
    even_leters = []
    for counter in range(0,len(message)):
        if is_even(counter):
            even_leters.append(message[counter])
    return even_leters

def get_odd_leters(message):
    odd_leters = []
    for counter in range(0,len(message)):
        if not is_even(counter):
            odd_leters.append(message[counter])
    return odd_leters
def swap_leters(message):
    leter_list = []
    if not is_even(len(message)):
        message=message + 'X'
    even_leters = get_even_leters(message)
    odd_leters = get_odd_leters(message)
    for counter in range(0,int(len(message)/2)):
        leter_list.append(odd_leters[counter])
        leter_list.append(even_leters[counter])
    new_message = ''.join(leter_list)
    return new_message
        
root=Tk()
root.withdraw()

while True:
    task = get_task()
    if task == 'encrypt':
        message = get_message()
        encrypted = swap_leters(message)
        messagebox.showinfo('Cliphertext of the secret is: ',encrypted)
    elif task == 'decrypt':
        message = get_message()
        decrypted = swap_leters(message)
        messagebox.showinfo('Plaintext of the secret is: ',decrypted)
    else:
        break

root.mainloop()

    
