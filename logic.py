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
        data_list = []
        for _, record in self.data.items():
            d = {record.name.value: {'name': record.name.value, 'phones': record.phones, 'birthday': f'{str(record.birthday)}'}}
            data_list.append(d)

        with open(self.filename, 'w') as file:
            json.dump(data_list, file, indent=4)

        return data_list
    
    def deserialize(self):
        try:
            with open(self.filename, 'r') as file:
                content = json.load(file)
                for elements in content:
                    for key, value in elements.items():
                        rec = Record(value['name'])
                        for phone in value['phones']:
                            rec.add_phone(phone)
                        
                        rec.birthday = value['birthday']
                    self.add_record(rec)
        except FileNotFoundError:
            pass
    
    def search(self, word):
        users = []
        if self.data is {}:
            return 'You data is empty'
        
        for key, value in self.data.items():
            mini_s = f'{value.name}{"".join(value.phones)}' 
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
        return self.value
    
    @phone.setter
    def phone(self, new_phone):
        self.value = new_phone
    
    def normalize(self):
        phone = self.value

        if len(phone) == 13 and phone.startswith('+380'):
            number = phone
        elif len(phone) == 12 and phone.startswith('380'):
            number = '+' + phone
        elif len(phone) == 11 and phone.startswith('80'):
            number = '+3' + phone
        elif len(phone) == 10 and phone.startswith('0'):
            number = '+38' + phone
        else:
            raise ValidatePhone('This is not correct phone number!')
    
        return number

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    @property
    def birthday(self):
        if self.value is None:
            return None
        
        splitter = None
        for char in self.value:
            if char in ['.', '/', '-', ',', ' ']:
                splitter = char
                break
        
        if splitter != None:
            days, month, year = self.value.split(splitter)

            return datetime(day=int(days), month=int(month), year=int(year)).date()
                
        raise ValidateBirthday('Not validate birthday!')
    
    @birthday.setter
    def birthday(self, date):
        self.value = date
        
    def __str__(self):
        return str(self.value)
    
class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday).birthday

    def add_phone(self, phone):
        for el in self.phones:
            if el == phone:
                return f'Phone with number {phone} already exist!'
        
        self.phones.append(str(Phone(phone.normalize()).phone))
        return f'Phone {phone} successfuly added!'
    
    def remove_phone(self, phone):
        if phone in self.phones:
            for index, el in enumerate(self.phones):
                if el == phone:
                    del self.phones[index]
                    return f'Phone {phone} was deleted!'

        return f'Sorry this number is not exist!' 

    def edit_phone(self, old_phone, new_phone):
        if old_phone in self.phones:
            for index, number in enumerate(self.phones):
                if old_phone == number:
                    self.phones[index] = Phone(new_phone).phone
                    return f'Phone with number {old_phone} successfully change at {new_phone}'
            
        return f'Number with {old_phone} not found!'
    
    def days_to_birthday(self):
        if self.birthday is None:
            print('You need set birthday first!')
            return ''
        
        splitter = None
        for char in str(self.birthday):
            if char in ['.', '/', '-', ',', ' ']:
                splitter = char
                break
                
        user_year, user_month, user_day = str(self.birthday).split(splitter)
        today = datetime.today()
        user_birthday = datetime(year=int(user_year), month=int(user_month), day=int(user_day))

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
