class Student:
    '''
    This class is for a student who has used library
    
    '''
    def __init__(self, name):

        self.name = name
        self.borrowed = {}
        self.returned = {}

    # getters
    def get_name(self):
        '''
        Getting the name of the student

        Returns str of student 
        '''
        return self.name

    def get_borrowed(self):
        '''
        Getting the dictionary of books the student has borrowed

        Returns dict of borrowed books
        '''
        return self.borrowed

    def get_returned(self):
        '''
        Getting the dictionary of books the student has returned
    
        Returns dict of returned books
        '''

        return self.returned

    # setters
    def add_borrowed(self, book_id, when, due):
        '''
        This adds a key and value to the dictionary of books the student has borrowed
    
        '''
        self.borrowed[book_id] = {'when': int(when), 'due': int(due)}

    def add_returned(self, book_id, when, state):
        '''
        This adds a key-value pair to the dictionary of books the student has returned

        '''
        self.returned[book_id] = {'when': int(when), 'state': int(state)}

class Database:
    '''
    The Database object contains classrooms dictionaries with Student objects
    '''
    def __init__(self):
       
        self.database = {}
        self.init_students()
        self.init_borrowed_books()
        self.init_returned_books()

    
    def get_database(self):
        '''
        Getting the method for the database dictionary

        Returns: dict of database
        '''
        return self.database

    # initialization of objects
    def init_students(self):
        '''
        Populates the database dict with classroom dicts containing student objects, reading data from students.txt
    
        Returns none
        '''
        with open('students.txt') as file:
            lines = file.read().splitlines()
            for student in lines:
                student = student.split(',')
                student_id = student[0]
                name = student[1]
                classroom = student[2]

                # Create classroom dict in database on first run
                if classroom not in self.database:
                    self.database[classroom] = {}

                # Create a new student and add them to their respective classroom based on the data from students.txt
                self.database[ classroom ][ student_id ] = Student(name)

    def init_borrowed_books(self):
        '''
        Populates the borrowed dict of each student with their borrowed books
        by matching their student ID with known borrowed books in borrowers.txt
      
        Returns none
        '''
        with open('borrowers.txt') as file:
            lines = file.read().splitlines()
            for loan in lines:
                loan = loan.split(';')

                for students in self.database.values():
                    for student_id, student in students.items():
                        if(student_id == loan[1]):  # If student in iteration matches ID present in borrowers.txt, add to returned books
                            student.add_borrowed( loan[0], loan[2], loan[3] )

    def init_returned_books(self):
        '''
        Populates the returned dict of each student with their returned books
        by matching their student ID with known returned books in returns.txt
        
        Returns none
        '''
        with open('returns.txt') as file:
            lines = file.read().splitlines()
            for returned in lines:
                returned = returned.split(';')
                
                for students in self.database.values():
                    for student_id, student in students.items():
                        if(student_id == returned[1]):  # If student in iteration matches ID present in returns.txt, add to returned books
                            student.add_returned( returned[0], returned[2], returned[3] )

class Library:
    '''
    The Library object represents all books available for borrowing in the librar
    
    '''
    def __init__(self):
        '''
        The constructor for the Library class
        
        '''
        self.library = {}
        with open('books.txt') as file:
            lines = file.read().splitlines()
            for book in lines:
                book = book.split('#')
                
                self.library[book[0]] = {
                        'name': book[1],
                        'author': book[2],
                        'price': float(book[3])
                        }

    def get(self):
        '''
        Getter for the library object
        Returns: dict of books in library
        '''
        return self.library

class TableFactory:
    
    def __init__(self, library, students, file):
        '''
        The constructor for the TableFactory class

        '''
        self.library = library
        self.students = students
        self.file = file

    def display_unreturned(self):
        '''
        Writes a table of all unreturned books, who has borrowed them, when they are due, and the total number of books unreturned by a classroom
      
        Returns none
        '''
        def divider():
            '''
            Writes a divider to file
    
            Returns none
            '''
            self.file.write(f"+{'-'*18}+{'-'*37}+{'-'*14}+" + '\n')

        def date_from_timestamp(timestamp):
            '''
            Converts the library's timestamp format into a more readable date with month names
        
            '''
            months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            timestamp = str(timestamp)
            input_year = '20' + timestamp[:2]
            input_month = months[int(timestamp[2:4])]
            input_day = timestamp[4:6]
            return f'{input_month} {input_day}, {input_year}'

        ## Header
        divider()
        self.file.write(f"| {'Student Name': <16} | {'Book': <35} | {'Due Date': <12} |" + '\n')
        divider()

        ## Rows
        total_outstanding_books = 0
        for student_id, student in sorted(self.students.items(), key=lambda item: item[1].get_name()):  # lambda function is to sort by Student name instead of key
            # list books that were borrowed and not returned
            for borrowed, data in student.get_borrowed().items():
                if borrowed not in student.get_returned():
                    total_outstanding_books += 1

                    book_name = self.library.get()[borrowed]['name']
                    due_date = date_from_timestamp( data['due'] )
                    self.file.write(f"| {student.get_name(): <16.16} | {book_name: <35.35} | {due_date: <12.12} |" + '\n')

        ## Totals
        divider()
        self.file.write(f"| {'Total Books': <54} | {total_outstanding_books: >12} |" + '\n')
        print(f'Total books currently borrowed: {total_outstanding_books}')
        divider()

    def display_debts(self):
        '''
        Writes a table of all students who owe money to the library, and total money owed by a classroom
        Returns none
        '''

        def divider():
            '''
            Writes a divider to file
            Returns none
            '''
            self.file.write(f"+{'-'*18}+{'-'*10}+" + '\n')

        ## Header
        divider()
        self.file.write('| Student Name     | Due      |' + '\n')
        divider()

        ## Rows
        total_owed = 0
        debts = {}
        for student_id, student in self.students.items():
            for returned, data in student.get_returned().items():
                # If the state of the returned book is not 0, 1, 2 (so either 1 or any other value)
                # then student owes the cost of the book
                if(data['state'] != 0 and data['state'] != 2 and data['state'] != 3):
                    owed = self.library.get()[returned]['price']
                    total_owed += owed

                    # Debts being a dict is such that the total price of all books owed by the
                    # same student can be summed, instead of having repeat entries
                    if student.get_name() not in debts:
                        debts[student.get_name()] = owed
                    else:
                        debts[student.get_name()] += owed

        # Display all students in debt on a table, sorted alphabetically by name
        for name in sorted(debts):
            debt = f'${debts[name]:.2f}'
            self.file.write(f"| {name: <16.16} | {debt: >8} |" + '\n')

        ## Totals
        divider()
        total_owed = f"${total_owed:.2f}"
        self.file.write(f"| {'Total Books': <16} | {total_owed: >8} |" + '\n')
        print(f'Total amount due for books: {total_owed}')
        divider()
        self.file.write('\n')
        print()

def main():
    with open('standing.txt', 'w') as f:
        db = Database()
        library = Library()

        # Write all tables to file for each classroom, sorted alphabetically
        for room, students in sorted(db.get_database().items()):
            class_str = 'Class: ' + room
            f.write(class_str + '\n')
            print(class_str)

            tblf = TableFactory(library, students, f)
            tblf.display_unreturned()
            tblf.display_debts()

main()