from datetime import datetime
import random

from logic import AddressBook, Record, ValidateBirthday, ValidatePhone

CONTACTS = AddressBook()

# DECORATOR
def input_error(func):
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except KeyError as e:
            return f"User {e} is not exist! Please add user before using this command!"
        except ValueError:
            return 'Give me name and phone please!'
        except IndexError:
            return 'You enter not corrent name or this name is not exist!'
        except TypeError:
            return 'Please enter name and phone!'
        except ValidateBirthday as e:
            return f'{e} - You enter not validate birthday! Must be <day>.<month>.<year>'
        except ValidatePhone:
            return 'You enter not validate phone! Must started with [+380, 380, 80, 0] and length of number = 13'
        except StopIteration:
            return 'Pagination end!'
    return inner

def command_hello(*args):
    return 'How can I help you?'

def command_load(contacts: AddressBook):
    contacts.deserialize()
    return ''

def command_save(contacts: AddressBook):
    contacts.serialize()
    return ''

def command_search(contacts: AddressBook, *args):
    return contacts.search(args[0])

@input_error
def command_add_user(contacts: dict, name, *args):
    if name in contacts:
        return f'Sorry, but contact with name {name.title()} already exist! Please try another name!'
    else:
        record = Record(name)
        
        if args:
            for phone in args:
                record.add_phone(phone)
        
        contacts.add_record(record)
        return f'User {name.title()} successfully added!'

@input_error
def command_add_phone(contacts: dict, name, phone):
    if name not in contacts:
        raise KeyError(name)
    record = contacts[name]

    if phone in record.phones:
        return f'Sorry, but phone with number {phone} already exist!'

    record.add_phone(phone)
    contacts.add_record(record)
    return f'Phone {phone} successfully added for user {str(name).title()}.'

@input_error
def command_set_birthday(contacts: dict, name, birthday):
    if name not in contacts:
        raise KeyError(name)
    
    record = contacts[name]

    splitter = None
    for char in birthday:
        if char in ['.', '/', '-', ',', ' ']:
            splitter = char
            break

    if splitter != None:
        days, month, year = birthday.split(splitter)

        birthday = datetime(day=int(days), month=int(month), year=int(year)).date()
    else:
        raise ValidateBirthday(birthday)
    
    record.birthday = birthday
    contacts.add_record(record)
    return f'Birthday successfully set for user {str(name).title()}.'

@input_error
def command_days_to_birthday(contacts: dict, name):
    if name not in contacts:
        raise KeyError(name)
    
    record = contacts[name]
    record.days_to_birthday()
    return ''

@input_error
def command_view_contacts(contacts: dict):
    if len(contacts) < 5:
        command_show_all(contacts)
    else:
        for name in contacts.__next__():
            record = contacts[name]
            print(f'{record.name.value}')
            print(f'   Phones: {", ".join([phone for phone in record.phones])}')
            print(f'   Birthday: {record.birthday}')
            print('---------')
        return ''

@input_error
def command_delete_phone(contacts: dict, name, phone):
    if name not in contacts:
        return f'Sorry but {name} not found!'
    
    record = contacts[name]

    if phone in record.phones:
        record.remove_phone(phone)
        contacts.add_record(record)
        return f'Phone {phone} successfully deleted for user {str(name).title()}.'
    
    return f'User {str(name).title()} don\'t have this number {phone}'

@input_error
def command_change(contacts: dict, name, old_phone, new_phone):
    if name not in contacts:
        raise KeyError(name)
    
    record = contacts[name]
    record.edit_phone(old_phone, new_phone)
    contacts.add_record(record)
    return f'Phone number {old_phone} has been changed to {new_phone} for {str(name).title()}.'

@input_error
def command_phone(contacts: dict, name):
    if name not in contacts:
        raise KeyError(name)
    record = contacts[name]
    
    print(f'{str(record.name.value).title()}')
    print(f'   Phones: {", ".join([phone for phone in record.phones])}')
    print('---------')
    return ''

@input_error
def command_generate_contacts(contacts: dict, count_contacts):
    if len(contacts) == 0:
        for i in range(int(count_contacts)):
            number = '+380'
            number += str(random.choices(['66', '50', '63', '96', '93', '67'])[0])
            number += ''.join([str(random.randint(0, 9)) for _ in range(7)])
            print(command_add_user(contacts, f'user_{i+1}', number))
    else:
        print('Please restart your app! And generate contacts when you dont have any contacts!')
            
    
    return ''

def command_show_all(contacts: dict):
    print(len(contacts))
    for s in contacts:
        for key, value in s.items():

            print(f'Name: {value.name.value}')
            print(f'Phones: {",".join([number for number in value.phones])}')
            print(f'Birthday: {value.birthday}')
            print('---------')
    
    return ''

def command_unknown(command):
    return f'Command [{command}] is not exist!'

COMMANDS = {
    'hello': command_hello,
    'search': command_search,
    'add user': command_add_user,
    'add phone': command_add_phone,
    'delete phone': command_delete_phone,
    'set birthday': command_set_birthday,
    'days to birthday': command_days_to_birthday,
    'view': command_view_contacts,
    'change': command_change,
    'phone': command_phone,
    'generate': command_generate_contacts,
    'show all': command_show_all
}

def main():
    print('For quick test. We can use command [generate <count contacts>]')
    command_load(CONTACTS)
    while True:
        command = input('Enter command: ').lower()
        if command in ['exit', 'good bye', 'close']:
            command_save(CONTACTS)
            print('Good bye!')
            break
        if command:
            current_command = filter(lambda comanda: command.startswith(comanda), [c for c in COMMANDS.keys()])
            func = ''
            
            try:
                func = command[:len(list(current_command)[0])]
            except IndexError:
                pass
            
            if COMMANDS.get(func):
                handler = COMMANDS.get(func)
                data = command[len(func):].strip()

                if data:  
                    data = data.split(' ')
                result = handler(CONTACTS, *data)
            else:
                result = command_unknown(command)  
            print(result, '\n')
        else:
            print('Please write something!', '\n')


if __name__ == '__main__':
    main()
