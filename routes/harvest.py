import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
import tornado.httpclient as httpclient
import logging
import csv
import time
import datetime
from routes.data import *
from storm.locals import *
from tornado.options import define, options


class UpdateHarvest(tornado.web.RequestHandler):
    def get(self):
        self.render("upload_form.html")
    
    def post(self):

        original_file = self.request.files['harvest-csv'][0]
        random_number = str(int(time.time()))

        #save file to local
        original_fname = original_file['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = random_number + '-Input'
        final_filename= fname+extension
        output_file = open("uploads/" + final_filename, 'w')
        output_file.write(original_file['body'])

        #open and parse
        local_file = open("uploads/" + final_filename, 'rU')
        reader = csv.DictReader(local_file, dialect='excel', quoting=csv.QUOTE_ALL)

        reader_keys = ['Date', 'Client', 'Project', 'Task', 'First name', 'Last name', 'Hours', 'Billable']
        remade_fname = random_number + '-Output'

        remade_output_filename = remade_fname + extension
        remade_output = open("uploads/" + remade_output_filename, 'w+')
        writer = csv.DictWriter(remade_output, delimiter=',', fieldnames=reader_keys, extrasaction='ignore')
        
        headers = {} 
        for n in reader_keys:
            headers[n] = n

        writer.writerow(headers)

        for row in reader:
            writer.writerow(row)
        remade_output.close()


        #reopen and parse
        local_file = open("uploads/" + remade_output_filename, 'rU')
        reader = csv.DictReader(local_file, quoting=csv.QUOTE_ALL)

        unique_names = set()
        unique_clients = set()
        unique_projects = set()

        update_messages = []


        database = create_database("sqlite:report-three.db")
        store = Store(database)

        # pass through the csv, looking for unique top-level objects
        for row in reader:
            this_name = str(row['First name']) + "|" + str(row['Last name'])
            unique_names.add(this_name)
            print(this_name)
            
            this_client = str(row['Client'])
            unique_clients.add(this_client)

            this_project = str(row['Client']) + "|" + str(row['Project'])
            unique_projects.add(this_project)


        # run through the unique names in the report, adding new names to the db
        for person in unique_names:
            clean_name = person.split("|")
            clean_first = clean_name[0]
            clean_last = clean_name[1]
            clean_full = clean_first + " " + clean_last
            clean_full_u = unicode(clean_full)

            is_new = store.find(Employee, Employee.full_name==clean_full_u)
            if is_new.count() == 0:
                employee = Employee()
                employee.first_name = unicode(clean_first)
                employee.last_name = unicode(clean_last)
                employee.full_name = clean_full_u

                store.add(employee)
                update_messages.append('>> added Employee: ' + clean_full)
            store.flush()

        # run through unique clients, adding to db so that they will be there to associate any new projects

        for client_loop in unique_clients:
            client_u = unicode(client_loop)

            is_new = store.find(Client, Client.client_name==client_u)

            if is_new.count() == 0:
                client = Client()
                client.client_name = client_u

                store.add(client)
                store.flush()
                update_messages.append('>> added Client: ' + client_loop)


        # run through the unique projects in the report, associating with the appropriate client
        
        for project_loop in unique_projects:
            project_split = project_loop.split("|")
            project_client = project_split[0]
            project_name = project_split[1]

            project_client_id = store.find(Client.client_id, Client.client_name==unicode(project_client)).one()
            project_exists = store.find(Project, Project.client_id==project_client_id, Project.project_name==unicode(project_name))

            if project_exists.count() == 0:
                project_create = Project()
                project_create.client_id = project_client_id
                project_create.project_name = unicode(project_name)

                store.add(project_create)
                store.flush()
                update_messages.append('>> added Project: ' + project_client + ' - ' + project_name)

        store.commit()


        local_file.close()

        local_file = open("uploads/" + remade_output_filename, 'rU')
        reader_two = csv.DictReader(local_file, quoting=csv.QUOTE_ALL)

        rows_read = 0

        for moolah in reader_two:
            rows_read += 1
            client_u = unicode(moolah['Client'])
            project_u = unicode(moolah['Project'])
            first_u = unicode(moolah['First name'])
            last_u = unicode(moolah['Last name'])

            print(str(rows_read) + " " + str(moolah['First name']) + " " + str(moolah['Last name'])) 
            #emp_count = store.find(Employee, And(Employee.first_name==first_u, Employee.last_name==last_u))
            #print("Query Count: " + str(emp_count.count()))

            # Basic Reference
            this_client = store.find(Client, Client.client_name==client_u).one()
            this_project = store.find(Project, And(Project.client_id==this_client.client_id, Project.project_name==project_u)).one()
            this_employee = store.find(Employee, And(Employee.first_name==first_u, Employee.last_name==last_u)).one()
            this_task = moolah['Task']
                       

            # Process Dates
            strip_date_slash = moolah['Date'].split('-')

            # crunch back into a single str
            date_string = str()
            for part in strip_date_slash:
                date_string += part
            date_int = int(date_string)

            year = int(date_string[:4])
            month = int(date_string[4:6])
            day = int(date_string[6:8])

            booking_date = datetime.date(year, month, day)
            booking_week_of = booking_date - datetime.timedelta(days=booking_date.weekday())


            week_of_split = str(booking_week_of).split('-')
            week_of_str = str()
            for part in week_of_split:
                week_of_str += part
            week_of_int = int(week_of_str)           

            # Check billable type and exceptions
            original_billable = moolah['Billable']
            
            billable_hours = 0.0
            nonbill_hours = 0.0
            exception_hours = 0.0
            pto_hours = 0.0


            if moolah['Hours'] is not None:
# Ghetto Rigged!  Revisit with real Exceptions model
                if original_billable != 'billable':
                    if moolah['Task'] == 'Account Management':
                        exception_hours = float(moolah['Hours'])
                    elif moolah['Task'] == 'Paid time-off':
                        pto_hours = float(moolah['Hours'])
                        #print(moolah['Hours'])
                    else:
                        nonbill_hours = float(moolah['Hours'])
                else:
                    billable_hours = float(moolah['Hours'])


            # Check for unique booking
            booking_exists = store.find(Booking, 
                Booking.date==date_int, 
                Booking.project_id==this_project.project_id, 
                Booking.employee_id==this_employee.employee_id,
                Booking.task_name==unicode(this_task))

            if booking_exists.count() == 0:
                # does not exist, process
                add_booking = Booking()
                add_booking.date = date_int
                add_booking.week_of = week_of_int
                add_booking.client_id = this_client.client_id
                add_booking.project_id = this_project.project_id
                add_booking.employee_id = this_employee.employee_id
                add_booking.task_name = unicode(this_task)
                add_booking.billable_total = billable_hours
                add_booking.nonbill_total = nonbill_hours
                add_booking.exception_total = exception_hours
                add_booking.pto_total = pto_hours

                store.add(add_booking)
                store.flush()

            else:
                #does exist, update the record
                booking_exists.set(billable_total=billable_hours, nonbill_total=nonbill_hours, exception_total=exception_hours, pto_total=pto_hours)
                store.flush()

        store.commit()

        print("Rows Read: " + str(rows_read) + " Unicodes: " + str(unicode_count) + " Ints: " + str(int_count))
            


        self.render("upload_form.html", messages=update_messages)
