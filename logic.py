from collections import UserDict
from datetime import datetime
import json
from pathlib import Path
import sys

class ValidatePhone(Exception):
    pass
class ValidateBirthday(Exception):
    pass

class AddressBook(UserDict):
    filename = Path('contacts.json')

    def __init__(self, data=None):
        super().__init__(data)
        self.elements_per_page = 5
        self.current_page = 1
    
    def add_record(self, record):
        self.data[record.name.value] = record

    def show_all(self):
        if self.data is {}:
            return 'Data is empty!'
        count_user = 0
        for key, value in self.data.items():
            count_user += 1
            print(f'-----[{count_user}]')
            print(f'Name: {value.name}')
            print(f'Phones: {", ".join([p.phone for p in value.phones])}')
            print(f'Birthday: {value.birthday}')
            print()
    
    def __iter__(self):
        self.current_page = 1
        return self

    def __next__(self):
        start_index = (self.current_page - 1) * self.elements_per_page
        end_index = start_index + self.elements_per_page
        keys = list(self.data.keys())
        if start_index >= len(keys):
            raise StopIteration
        page_keys = keys[start_index:end_index]
        page_records = {key: self.data[key] for key in page_keys}
        self.current_page += 1
        return page_records

    def serialize(self):
        if self.data is not {}:
            data_list = []
            for _, record in self.data.items():
                d = {record.name.value: {'name': record.name.value, 'phones': [record.phones[i].phone for i in range(len(record.phones))], 'birthday': str(record.birthday)}}
                data_list.append(d)

            with open(self.filename, 'w') as file:
                json.dump(data_list, file, indent=4)

            return data_list
        return ''
    
    def deserialize(self):
        try:
            if self.data is not {}:
                with open(self.filename, 'r') as file:
                    content = json.load(file)
                    for elements in content:
                        for key, value in elements.items():
                            rec = Record(value['name'])
                            for phone in value['phones']:
                                rec.add_phone(phone)
                            rec.birthday = value['birthday']

                        self.add_record(rec)
            
            return ''
        except FileNotFoundError:
            pass
    
    def search(self, word):
        users = []
        if self.data is {}:
            return 'You data is empty'
        
        for key, value in self.data.items():
            mini_s = f'{value.name}{"".join([p.phone for p in value.phones])}' 
            if mini_s.find(word) != -1:
                users.append(key)
        
        if len(users) > 0:
            return users
        
        return f'No results found for “{word}”'


# ----
class Field:
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return str(self.value)
        
class Name(Field):
    pass

class Phone(Field):
    
    @property
    def phone(self):
        return self.normalize(self.value)
    
    @phone.setter
    def phone(self, new_phone):
        self.value = self.normalize(new_phone)
    
    def normalize(self, p):
        if len(p) == 13 and p.startswith('+380'):
            number = p
        elif len(p) == 12 and p.startswith('380'):
            number = '+' + p
        elif len(p) == 11 and p.startswith('80'):
            number = '+3' + p
        elif len(p) == 10 and p.startswith('0'):
            number = '+38' + p
        else:
            raise ValidatePhone(f'This is not correct {p} phone number! ')
    
        return number
    
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'Phone({self.value})'

class Birthday(Field):

    @property
    def birthday(self):
        return self.value
    
    @birthday.setter
    def birthday(self, date):
        self.value = date

    def normalize_birthday(self):
        if self.value is None:
            return None
        
        splitter = None
        for char in self.value:
            if char in ['.', '/', '-', ',', ' ']:
                splitter = char
                break
        
        if splitter is not None:
            if self.value.count(splitter) > 2:
                raise ValidateBirthday('Not validate birthday! Format date: <day>.<month>.<year>')

            day, month, year = self.value.split(splitter)

            day = ''.join(list(filter(str.isdigit, day)))
            month = ''.join(list(filter(str.isdigit, month)))
            year = ''.join(list(filter(str.isdigit, year)))
            
            try:
                return datetime(day=int(day), month=int(month), year=int(year)).date()
            except ValueError:
                raise ValidateBirthday('Day or month or year is out of range!')
        
        raise ValidateBirthday('Not validate birthday! Format date: <day>.<month>.<year>')

    def __str__(self):
        return str(self.value)
    
class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday).normalize_birthday()        

    def get_or_none(self, phone):
        phone = Phone(phone)
        if isinstance(phone, Phone):
            phone = phone.value
        for p in self.phones:
            if p.value == phone:
                return p

    def add_phone(self, phone):
        number = Phone()
        number.phone = number.normalize(phone)
    
        p = self.get_or_none(number.phone)
        if p is None:
            self.phones.append(number)
            return f'Number {phone} successfully added!'
        
        return f'Number {phone} already exist!'
    
    def remove_phone(self, phone):
        number = Phone()
        number.phone = phone

        p = self.get_or_none(number.phone)
        if p is None:
            return f'Sorry this number [{phone}] is not exist!'
        
        self.phones.remove(p)
        return f'Phone {phone} was deleted!'

    def edit_phone(self, old_phone, new_phone):
        old_number = Phone()
        old_number.phone = old_phone

        p = self.get_or_none(old_number.phone)
        
        if p is None:
            return f'Sorry this number [{old_phone}] is not exist!'

        new_number = Phone()
        new_number.phone = new_phone

        self.phones[self.phones.index(p)] = new_number
    
        return f'Number from {old_phone} to {new_phone} successfully change!'
        
    def days_to_birthday(self):
        if self.birthday is None:
            print('You need set birthday first!')
            return ''
        
        today = datetime.today()
        user_birthday = datetime(year=int(self.birthday.year), month=int(self.birthday.month), day=int(self.birthday.day))

        delta_user_birthday = user_birthday.replace(year=today.year)
        if delta_user_birthday < today:
            delta_user_birthday = delta_user_birthday.replace(year=today.year + 1)

        delta = delta_user_birthday - today
        delta_days = delta.days

        print(f"To birthday {int(delta_days)+1} days!")
        return ''

    def __repr__(self) -> str:
        return f'Record({self.name}, {self.phones}, {self.birthday})'
    

if __name__ == '__main__':
    pass
